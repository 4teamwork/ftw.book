from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.utils import flaten_tree
from ftw.book.interfaces import IBook
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.publisher.browser import BrowserView


class ReaderView(BrowserView):

    def __call__(self):
        self.book = self.get_book_obj()
        self.tree = self.get_tree(self.book)
        self.structure = flaten_tree(self.tree)
        super(ReaderView).__call__(self)

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
