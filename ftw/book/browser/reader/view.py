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


RENDER_BLOCKS_PER_REQUEST_THRESHOLD = 4
_marker = object()


class ReaderView(BrowserView):

    template = ViewPageTemplateFile('templates/reader.pt')
    navigation_recurse = ViewPageTemplateFile(
        'templates/navigation_recurse.pt')

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

    def render_next(self, block_render_threshold=_marker):
        """Renders the next blocks.
        """
        if block_render_threshold == _marker:
            block_render_threshold = RENDER_BLOCKS_PER_REQUEST_THRESHOLD

        after_uid = self.request.get('after_uid', '')
        loaded_uids = self.request.get('loaded_blocks[]', [])
        insert_after = after_uid or 'TOP'

        data = []

        brainlist = flaten_tree(self.tree)

        found = False

        for brain in brainlist:
            if not found and after_uid == '' and \
                    brain.UID == self.context.UID():
                found = True

            if not found and brain.UID == after_uid:
                found = True
                continue

            elif not found:
                continue

            elif found and brain.UID in loaded_uids:
                # we already have this block loaded
                break

            block_html = self.render_block(brain)
            if block_html:
                data.append([brain.UID, block_html])

            block_render_threshold -= 1
            if block_render_threshold == 0:
                break

        response_data = {'insert_after': insert_after,
                         'data': data,
                         'first_uid': data and data[0][0],
                         'last_uid': data and data[-1][0]}
        return dumps(response_data)

    def render_previous(self, block_render_threshold=_marker):
        """Render previous blocks.
        """
        if block_render_threshold == _marker:
            block_render_threshold = RENDER_BLOCKS_PER_REQUEST_THRESHOLD

        before_uid = self.request.get('before_uid', '')
        loaded_uids = self.request.get('loaded_blocks[]', [])
        insert_before = before_uid

        if before_uid == '' or not loaded_uids:
            # render_next should be called before render_previous, so there
            # should already content be loaded.
            return '{}'

        data = []

        brainlist = flaten_tree(self.tree)
        previous = []
        found = False

        for brain in brainlist:
            if brain.UID == before_uid:
                found = True
                break
            previous.insert(0, brain)

        if not found:
            return u'{}'

        while block_render_threshold > 0 and len(previous) > 0:
            brain = previous.pop(0)

            if brain.UID in loaded_uids:
                break

            block_html = self.render_block(brain)
            if block_html:
                data.insert(0, [brain.UID, block_html])

            block_render_threshold -= 1

        response_data = {'insert_before': insert_before,
                         'data': data,
                         'first_uid': data and data[0][0],
                         'last_uid': data and data[-1][0]}
        return dumps(response_data)

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

    def render_navigation(self, item=None):
        if item is None:
            item = self.get_toc_tree(self.tree)

        toc_title = item.get('item').Title

        if item.get('toc_number', None):
            toc_title = '%s %s' % (item.get('toc_number'), toc_title)

        return self.navigation_recurse(**{
                'item': item,
                'toc_title': toc_title,
                'children_ul_class': 'book-reader-navigation-%i' % (
                    item['depth'] + 1)})