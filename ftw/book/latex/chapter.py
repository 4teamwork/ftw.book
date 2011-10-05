from plonegov.pdflatex.browser.converter import LatexCTConverter
from ftw.book.latex import utils


class ChapterLatexConverter(LatexCTConverter):

    def __call__(self, context, view):
        super(ChapterLatexConverter, self).__call__(context, view)
        latex = utils.getLatexHeading(context, view)
        latex += self.convertChilds(context, view)
        return latex
