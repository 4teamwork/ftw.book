from Products.ATContentTypes.interfaces.link import IATLink
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class LinkLaTeXView(MakoLaTeXView):
    adapts(IATLink, Interface, Interface)

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
