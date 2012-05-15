from ftw.book.latex import utils
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.pdfgenerator.view import MakoLaTeXView
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.types.common.interfaces import IParagraph
from zope.component import adapts
from zope.interface import Interface


class ParagraphLaTeXView(MakoLaTeXView):
    adapts(IParagraph, Interface, Interface)

    def render(self):
        latex = []

        if self.context.getShowTitle():
            latex.append(utils.get_latex_heading(self.context, self.layout))

        text_latex = self.get_text_latex()
        floatable = text_latex and True or False
        image_latex = self.get_image_latex(floatable)

        latex.append(image_latex)
        latex.append(text_latex)

        return '\n'.join(latex)

    def get_text_latex(self):
        tex = ''
        text = self.context.getText().strip()
        if len(text) > 0:
            tex += self.convert(text)
            tex += '\n'
        return tex

    def get_image_latex(self, floatable):
        image = self.context.getImage()

        if not image or image.get_size() == 0:
            return ''

        image_layout = IBlockConfig(self.context).image_layout
        caption = self.context.getImageCaption()
        generator = ImageLaTeXGenerator(self.context, self.layout)

        return generator(image, image_layout, floatable=floatable,
                         caption=caption)
