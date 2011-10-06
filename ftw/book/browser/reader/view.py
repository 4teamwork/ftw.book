from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.utils import filter_tree
from ftw.book.browser.reader.utils import flaten_tree
from ftw.book.interfaces import IBook
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.publisher.browser import BrowserView


class ReaderView(BrowserView):

    def __call__(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)

        return super(ReaderView, self).__call__()

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
