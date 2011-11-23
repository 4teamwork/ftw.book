from ftw.book.interfaces import IBook
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapts
from zope.interface import Interface


class BookLaTeXView(RecursiveLaTeXView):
    adapts(IBook, Interface, Interface)

    def render(self):
        return self.render_children()
