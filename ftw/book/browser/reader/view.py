from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.utils import filter_tree
from ftw.book.browser.reader.utils import flaten_tree
from ftw.book.interfaces import IBook
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class ReaderView(BrowserView):

    toc_template = ViewPageTemplateFile('templates/toc_recurse.pt')

    def __call__(self):
        self.book = self.get_book_obj()
        self.tree = self.get_tree(self.book)
        self.structure = flaten_tree(self.tree)
        return super(ReaderView, self).__call__()

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

        return filter_tree(filterer, tree, copy=True)

    def render_toc(self, item=None):
        if item is None:
            item = self.get_toc_tree(self.tree)

        return self.toc_template(**{
                'item': item,
                'is_root': item.get('depth', -1) == 0,
                'li_class': 'book-toc-%s' % str(item.get('depth'))})

