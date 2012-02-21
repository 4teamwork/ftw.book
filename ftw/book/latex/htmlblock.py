from ftw.book.interfaces import IHTMLBlock
from ftw.book.latex import utils
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class HTMLBlockLaTeXView(MakoLaTeXView):
    adapts(IHTMLBlock, Interface, Interface)

    def render(self):
        latex = []

        if self.context.getShowTitle():
            latex.append(utils.get_latex_heading(self.context, self.layout))

        text = self.context.getText().strip()
        if len(text) > 0:
            latex.append(self.convert(text))

        latex.append('')
        return '\n'.join(latex)
