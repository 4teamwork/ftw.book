from ftw.book.interfaces import IBook
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapter
from zope.interface import Interface


@adapter(IBook, Interface, ILaTeXLayout)
class BookLaTeXView(RecursiveLaTeXView):

    def render(self):
        return self.render_children()
