from ftw.book.interfaces import IRemark, IAddRemarkLayer
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class RemarkLaTeXView(MakoLaTeXView):
    adapts(IRemark, IAddRemarkLayer, Interface)

    def render(self):

        self.layout.use_package('color')
        latex = []

        title = self.convert(self.context.Title())
        if title:
            latex.append('{\\bf %s}\\' % title)

        text = self.context.getText().strip()
        if len(text) > 0:
            latex.append(self.convert(text))

        latex.append('')

        return self.embed_in_grey_box('\n'.join(latex))

    def embed_in_grey_box(self, latex):
        """ Embed the given latex code in a grey box
        """

        color = r'\definecolor{light-gray}{gray}{0.8}'
        box_begin = r'\fcolorbox{black}{light-gray}{\parbox[r]{\textwidth}{'
        box_end = '}}'

        return color + box_begin + latex + box_end
