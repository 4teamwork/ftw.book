from plonegov.pdflatex.browser.converter import LatexCTConverter

class ChapterLatexConverter(LatexCTConverter):

    def __call__(self, context, view):
        super(ChapterLatexConverter, self).__call__(context, view)
        latex = '\\section{%s}' % context.Title()
        latex += self.convertChilds(context, view)
        return latex