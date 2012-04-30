from ftw.book.latex import utils
from ftw.book.latex.utils import get_raw_image_data
from ftw.pdfgenerator.view import MakoLaTeXView
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.types.common.interfaces import IParagraph
from zope.component import adapts
from zope.interface import Interface


class ParagraphLaTeXView(MakoLaTeXView):
    adapts(IParagraph, Interface, Interface)

    def render(self):
        latex = []

        # generate TITLE latex
        if self.context.getShowTitle():
            latex.append(utils.get_latex_heading(self.context, self.layout))

        image = self.context.getImage()
        if image or image != 0:
            latex.append(self.get_image_latex())

        # generate latex for field "text"
        latex.append(self.get_text_latex())
        return '\n'.join(latex)

    def get_text_latex(self):
        tex = ''
        text = self.context.getText().strip()
        if len(text) > 0:
            tex += self.convert(text)
            tex += '\n'
        return tex

    def get_image_latex(self):
        image = self.context.getImage()

        # test for image
        if not image or image.get_size() == 0:
            return ''

        # imageLayout
        imageLayout = IBlockConfig(self.context).image_layout
        width = r'\textwidth'
        command = ''
        align = ''
        caption = self.context.getImageCaption()

        if imageLayout == 'no-image':
            return ''

        elif imageLayout == 'small':
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
        tex = []

        if command == 'figure':
            tex.append(r'\begin{%s}[htbp]' % command)

        elif command == 'wrapfigure':
            tex.append(r'\begin{%s}{%s}{%s}' % (command, align, width))

        tex.append(r'\begin{center}')
        tex.append(r'\includegraphics[width=%s]{%s}' % (width, uid))
        tex.append(r'\end{center}')
        if caption:
            tex.append(r'\caption{%s}' % caption)
        tex.append(r'\end{%s}' % command)

        # register image
        self.layout.get_builder().add_file(
            '%s.jpg' % uid, get_raw_image_data(image))

        # register latex packages
        self.layout.use_package('graphicx')
        self.layout.use_package('wrapfig')
        return '\n'.join(tex)
