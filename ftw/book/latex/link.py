from ftw.pdfgenerator.view import MakoLaTeXView
from Products.ATContentTypes.interfaces.link import IATLink
from zope.component import adapter
from zope.interface import Interface


@adapter(IATLink, Interface, Interface)
class LinkLaTeXView(MakoLaTeXView):

    def render(self):
        latex = []
        latex.append(r'\begin{description}')

        title = self.convert(self.context.Title())
        url = r'\href{%s}{%s}' % (
            self.convert(self.context.remoteUrl),
            self.convert(self.context.remoteUrl))

        latex.append(r'\item[%s (%s)]{%s}' % (
                title, url, self.convert(self.context.getRawDescription())))

        latex.append(r'\end{description}')
        return '\n'.join(latex)
