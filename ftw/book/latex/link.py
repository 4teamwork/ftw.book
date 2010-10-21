from plonegov.pdflatex.browser.converter import LatexCTConverter


class LinkLatexConverter(LatexCTConverter):

    def __call__(self, context, view):
        super(LinkLatexConverter, self).__call__(context, view)
        latex = []
        latex.append(r'\begin{description}')
        title = view.convert(self.context.Title())
        url = r'\href{%s}{%s}' % (
            view.convert(self.context.remoteUrl),
            view.convert(self.context.remoteUrl))
        latex.append(r'\item[%s (%s)]{%s}' % (
            title, url, view.convert(self.context.getRawDescription())))
        latex.append(r'\end{description}')
        return '\n'.join(latex)
