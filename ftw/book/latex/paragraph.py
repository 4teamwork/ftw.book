from plonegov.pdflatex.browser.converter import LatexCTConverter
from simplelayout.base.interfaces import IBlockConfig

import utils

class ParagraphLatexConverter(LatexCTConverter):
    
    def __call__(self, context, view):
        super(ParagraphLatexConverter, self).__call__(context, view)
        latex = []
        # generate TITLE latex
        if context.getShowTitle():
            latex.append(utils.getLatexHeading(context, view))
        image = context.getImage()
        if image or image != 0:
			latex.append(self.getImageLatex(context, view))
        # generate latex for field "text"
        latex.append(self.getTextLatex(context, view))
        return '\n'.join(latex)

    def getTextLatex(self, context, view):
        tex = ''
        if len(context.getText().strip())>0:
            tex += view.convert(context.getText().strip())
            tex += '\n'
        return tex

    def getImageLatex(self, context, view):
        image = context.getImage()
        # test for image
        if not image or image.size==0:
            return ''
        # imageLayout
        imageLayout = IBlockConfig(context).image_layout
        width = ''
        command = ''
        align = ''
        caption = context.getImageCaption()
        if imageLayout=='no-image':
            return ''
        elif imageLayout=='small':
            command = 'wrapfigure'
            width = r'0.25\textwidth'
            align = 'l'
        elif imageLayout=='middle':
            command = 'wrapfigure'
            width = r'0.5\textwidth'
            align = 'l'
        elif imageLayout=='full':
            width = r'\textwidth'
            command = 'figure'
        elif imageLayout=='middle-right':
            command = 'wrapfigure'
            width = r'0.5\textwidth'
            align = 'r'
        elif imageLayout=='small-right':
            command = 'wrapfigure'
            width = r'0.25\textwidth'
            align = 'r'
        # generate latex
        uid = '%s_image' % context.UID()
        tex = []
        if command=='figure':
            tex.append(r'\begin{%s}[htbp]' % command)
        elif command=='wrapfigure':
            tex.append(r'\begin{%s}{%s}{%s}' % (command, align, width))
        tex.append(r'\begin{center}')
        tex.append(r'\includegraphics[width=%s]{%s}' % (width, uid))
        tex.append(r'\end{center}')
        tex.append(r'\caption{%s}' % caption)
        tex.append(r'\end{%s}' % command)
        # register image
        view.addImage(uid=uid, image=image)
        # register latex packages
        view.conditionalRegisterPackage('graphicx')
        view.conditionalRegisterPackage('wrapfig')
        return '\n'.join(tex)
