from plonegov.pdflatex.browser.converter import LatexCTConverter
from simplelayout.base.interfaces import IBlockConfig


class ImageLatexConverter(LatexCTConverter):

    def __call__(self, context, view):
        super(ImageLatexConverter, self).__call__(context, view)
        latex = []

        image = self.context.getImage()
        imageLayout = IBlockConfig(context).image_layout
        width = ''
        command = 'figure'
        align = ''

        caption = "%s: %s" % (
            view.convert(context.Title()),
            view.convert(context.description))

        if imageLayout == 'no-image':
            return ''

        elif imageLayout == 'small':
            width = r'0.25\textwidth'
            align = 'l'

        elif imageLayout == 'middle':
            width = r'0.5\textwidth'
            align = 'l'

        elif imageLayout == 'full':
            width = r'\textwidth'

        elif imageLayout == 'middle-right':
            width = r'0.5\textwidth'
            align = 'r'

        elif imageLayout == 'small-right':
            width = r'0.25\textwidth'
            align = 'r'

        # generate latex
        uid = '%s_image' % context.UID()
        if command == 'figure':
            latex.append(r'\begin{%s}[htbp]' % command)

        elif command == 'wrapfigure':
            latex.append(r'\begin{%s}{%s}{%s}' % (command, align, width))

        latex.append(r'\begin{center}')
        latex.append(r'\includegraphics[width=%s]{%s}' % (width, uid))
        latex.append(r'\end{center}')
        latex.append(r'\caption{%s}' % caption)
        latex.append(r'\end{%s}' % command)

        # register image
        view.addImage(uid=uid, image=image)

        # register latex packages
        view.conditionalRegisterPackage('graphicx')
        view.conditionalRegisterPackage('wrapfig')

        return '\n'.join(latex)
