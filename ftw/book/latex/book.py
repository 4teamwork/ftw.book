from ftw.book.interfaces import IBook
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapts
from zope.interface import Interface


class BookLaTeXView(RecursiveLaTeXView):
    adapts(IBook, Interface, ILaTeXLayout)

    def render(self):
        return self.render_children()
