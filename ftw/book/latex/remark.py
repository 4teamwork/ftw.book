from ftw.book.interfaces import IRemark, IAddRemarkLayer
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class RemarkLaTeXView(MakoLaTeXView):
    adapts(IRemark, IAddRemarkLayer, Interface)

    def render(self):
        latex = []
        title = self.convert(self.context.Title())

        if title:
            latex.append('{\\bf %s}\\' % title)

        text = self.context.getText().strip()
        if len(text) > 0:
            latex.append(self.convert(text))

        latex.append('')
        return '\n'.join(latex)
