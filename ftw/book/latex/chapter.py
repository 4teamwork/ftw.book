from plonegov.pdflatex.browser.converter import LatexCTConverter

import utils

class ChapterLatexConverter(ZugCTConverter):

    def __call__(self, context, view):
        super(ChapterLatexConverter, self).__call__(context, view)
		latex = '\\section{%s}' % context.Title())
		latex += self.convertChilds(context, view)
		return '\n'.join(latex)