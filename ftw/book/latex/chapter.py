from ftw.book.interfaces import IChapter
from ftw.book.latex import utils
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapts
from zope.interface import Interface


class ChapterLaTeXView(RecursiveLaTeXView):
    adapts(IChapter, Interface, Interface)

    def render(self):
        latex = utils.get_latex_heading(self.context, self.layout)
        latex += self.render_children()
        return latex
