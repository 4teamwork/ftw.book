from ftw.book.interfaces import IBookTextBlock
from ftw.book.latex import utils
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.simplelayout.interfaces import IBlockConfiguration
from zope.component import adapter
from zope.interface import Interface


@adapter(IBookTextBlock, Interface, Interface)
class TextBlockLaTeXView(MakoLaTeXView):

    def render(self):
        latex_title = ''
        if self.context.show_title:
            latex_title = utils.get_latex_heading(self.context, self.layout)

        latex_text = self.get_text_latex()
        latex_image = self.get_image_latex(bool(latex_text))
        return '\n'.join(
            filter(len,
                   map(str.strip, (latex_title,
                                   latex_image,
                                   latex_text)))).strip() + '\n\n'

    def get_text_latex(self):
        if not self.context.text:
            return ''
        return self.convert(self.context.text.output).strip()

    def get_image_latex(self, floatable):
        image = self.context.image

        if not image or not image.size:
            return ''

        sl_config = IBlockConfiguration(self.context).load()
        sl_scale = sl_config.get('scale', 'sl_textblock_small')

        if sl_scale == 'sl_textblock_large':
            image_layout = 'full'
            floatable = False
        else:
            if sl_scale == 'sl_textblock_small':
                image_layout = 'small'
            elif sl_scale == 'sl_textblock_middle':
                image_layout = 'middle'

            if sl_config.get('imagefloat', 'left') == 'right':
                image_layout += '-right'

        caption = self.context.image_caption
        generator = ImageLaTeXGenerator(self.context, self.layout)
        return generator(image, image_layout, floatable=floatable,
                         caption=caption)
