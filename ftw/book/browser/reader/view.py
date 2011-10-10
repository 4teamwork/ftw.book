from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.browser.reader.utils import filter_tree
from ftw.book.browser.reader.utils import flaten_tree
from ftw.book.browser.reader.utils import modify_tree
from ftw.book.interfaces import IBook
from json import dumps
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView


RENDER_BLOCKS_PER_REQUEST_THRESHOLD = 1
_marker = object()


class ReaderView(BrowserView):

    template = ViewPageTemplateFile('templates/reader.pt')

    def __call__(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)

        return self.template()

    @property
    def book(self):
        if not getattr(self, '_book', None):
            self._book = self.get_book_obj()
        return self._book

    @property
    def tree(self):
        if not getattr(self, '_tree', None):
            self._tree = self.get_tree(self.book)
        return self._tree

    def get_inline_javascript(self):
        options = self.get_javascript_options()
        return 'jq(function($) { init_reader_view(%s); });' % (
            dumps(options))

    def get_javascript_options(self):
        options = {
            'prev_uid': None,
            'next_uid': self.context.UID()}

        prev = None
        for brain in flaten_tree(self.tree):
            if brain.UID == self.context.UID():
                if prev:
                    options['prev_uid'] = prev.UID

                break

            else:
                prev = brain

        return options

    def render_next(self, block_render_threshold=_marker):
        """Renders the next blocks.
        """
        if block_render_threshold == _marker:
            block_render_threshold = RENDER_BLOCKS_PER_REQUEST_THRESHOLD

        next_uid = self.request.get('next_uid', '')

        html = []

        brainlist = flaten_tree(self.tree)
        for brain in brainlist:
            if len(html) == 0 and next_uid != '' and brain.UID != next_uid:
                continue

            block_html = self.render_block(brain)
            if block_html:
                html.append(block_html)

            block_render_threshold -= 1
            if block_render_threshold == 0:
                break

        try:
            next = brainlist.next()
        except StopIteration:
            next = None

        data = {'next_uid': next and next.UID or None,
                'html': '\n'.join(html)}
        return dumps(data)

    def render_previous(self, block_render_threshold=_marker):
        """Render previous blocks.
        """
        if block_render_threshold == _marker:
            block_render_threshold = RENDER_BLOCKS_PER_REQUEST_THRESHOLD

        previous_uid = self.request.get('previous_uid', '')

        html = []

        brainlist = flaten_tree(self.tree)
        previous = []
        found = False

        for brain in brainlist:
            previous.insert(0, brain)
            if previous_uid != '' and brain.UID == previous_uid:
                found = True
                break

        if not found:
            return u'{}'

        while block_render_threshold > 0 and len(previous) > 0:
            brain = previous.pop(0)
            block_html = self.render_block(brain)
            if block_html:
                html.insert(0, block_html)

            block_render_threshold -= 1

        data = {'previous_uid': previous and previous[0].UID or None,
                'html': '\n'.join(html)}
        return dumps(data)

    def render_block(self, brain):
        obj = brain.getObject()

        renderer = queryMultiAdapter((obj, self.request, self),
                                     IBookReaderRenderer)
        if not renderer:
            return ''

        else:
            return renderer.render()

    def get_tree(self, book):
        """Returns an unlimited, recursive navtree of the book.
        """
        query = {
            'path': '/'.join(book.getPhysicalPath())}

        return buildFolderTree(book, obj=book, query=query)

    def get_book_obj(self):
        obj = self.context

        while obj is not None:
            if IBook.providedBy(obj):
                return obj

            elif IPloneSiteRoot.providedBy(obj):
                raise Exception('Could not find book.')

            else:
                obj = aq_parent(aq_inner(obj))

        raise Exception('Could not find book.')

    def get_toc_tree(self, tree):
        """Returns a filtered tree for building a table of contents. Brains
        of sl-blocks with showTitle=False are removed.
        """

        def filterer(item):
            brain = item.get('item')
            if brain.portal_type in ('Book', 'Chapter'):
                return True

            else:
                return brain.showTitle

        tree = filter_tree(filterer, tree, copy=True)

        def toc_number_prefix_adder(node, parent):
            if not parent:
                # the book has no number
                node['toc_number'] = None

            elif not parent.get('toc_number', None):
                # first level - do not in include parent toc prefix
                node['toc_number'] = '%i' % (
                    parent.get('children').index(node) + 1)

            else:
                # second level or deeper - include parent number as prefix
                node['toc_number'] = '%s.%i' % (
                    parent.get('toc_number'),
                    parent.get('children').index(node) + 1)

        return modify_tree(toc_number_prefix_adder, tree)
