from plonegov.pdflatex.browser.converter import LatexCTConverter


class BookLatexConverter(LatexCTConverter):

    def __call__(self, context, view):
        super(BookLatexConverter, self).__call__(context, view)
        latex = ''
        latex += self.convertChilds(context, view)
        return latex
