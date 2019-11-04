from ftw.book.interfaces import IHTMLBlock
from ftw.book.latex import utils
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapter
from zope.interface import Interface


@adapter(IHTMLBlock, Interface, Interface)
class HTMLBlockLaTeXView(MakoLaTeXView):

    def render(self):
        latex = []

        if self.context.show_title:
            latex.append(utils.get_latex_heading(self.context, self.layout))

        content = (self.context.content or u'').strip()
        if content:
            latex.append(self.convert(content))

        latex.append('')
        return '\n'.join(latex)
