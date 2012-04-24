from Products.ATContentTypes.interfaces.image import IATImage
from ftw.book.latex.utils import get_raw_image_data
from ftw.pdfgenerator.view import MakoLaTeXView
from simplelayout.base.interfaces import IBlockConfig
from zope.component import adapts
from zope.interface import Interface


class ImageLaTeXView(MakoLaTeXView):
    adapts(IATImage, Interface, Interface)

    def render(self):
        latex = []

        image = self.context.getImage()
        imageLayout = IBlockConfig(self.context).image_layout
        width = r'\textwidth'
        command = 'figure'
        align = ''

        if imageLayout == 'no-image':
            return ''

        if self.context.Description():
            caption = self.convert(self.context.Description())
        else:
            caption = None

        if imageLayout == 'small':
            command = 'wrapfigure'
            width = r'0.25\textwidth'
            align = 'l'

        elif imageLayout == 'middle':
            command = 'wrapfigure'
            width = r'0.5\textwidth'
            align = 'l'

        elif imageLayout == 'full':
            width = r'\textwidth'
            command = 'figure'

        elif imageLayout == 'middle-right':
            command = 'wrapfigure'
            width = r'0.5\textwidth'
            align = 'r'

        elif imageLayout == 'small-right':
            command = 'wrapfigure'
            width = r'0.25\textwidth'
            align = 'r'

        # generate latex
        uid = '%s_image' % self.context.UID()
        if command == 'figure':
            latex.append(r'\begin{%s}[htbp]' % command)

        elif command == 'wrapfigure':
            latex.append(r'\begin{%s}{%s}{%s}' % (command, align, width))

        latex.append(r'\begin{center}')
        latex.append(r'\includegraphics[width=%s]{%s}' % (width, uid))
        latex.append(r'\end{center}')
        if caption:
            latex.append(r'\caption{%s}' % caption)
        latex.append(r'\end{%s}' % command)

        # register image
        builder = self.layout.get_builder()
        builder.add_file('%s.jpg' % uid, get_raw_image_data(image))

        # register latex packages
        self.layout.use_package('graphicx')
        self.layout.use_package('wrapfig')

        return '\n'.join(latex)
