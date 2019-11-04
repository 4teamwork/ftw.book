from ftw.book.interfaces import ITable
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapter
from zope.interface import Interface


@adapter(ITable, Interface, Interface)
class TableLaTeXView(MakoLaTeXView):

    def render(self):
        latex = []
        table = self.context.getTable()
        if len(table) > 0:
            latex.append(self.convert(table))

        if self.context.footnote_text and self.context.footnote_text.output:
            footnote_text = self.context.footnote_text.output.strip()
            latex.append(r'\vspace{0pt}')
            latex.append('{\\footnotesize %s}' % (
                self.convert(footnote_text.strip())))

        return '\n'.join(latex)
