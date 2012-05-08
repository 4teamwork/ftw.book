from ftw.book.interfaces import ITable
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class TableLaTeXView(MakoLaTeXView):
    adapts(ITable, Interface, Interface)

    def render(self):

        latex = []

        table = self.context.getTable()
        if len(table) > 0:
            latex.append(self.convert(table))

        footnote_text = self.context.getFootnoteText().strip()
        if len(footnote_text) > 0:

            latex.append(r'\vspace{0pt}')
            latex.append('{\\footnotesize %s}' % (
                    self.convert(footnote_text.strip())))

        return '\n'.join(latex)
