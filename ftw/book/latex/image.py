from Products.ATContentTypes.interfaces.image import IATImage
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.pdfgenerator.view import MakoLaTeXView
from simplelayout.base.interfaces import IBlockConfig
from zope.component import adapts
from zope.interface import Interface


class ImageLaTeXView(MakoLaTeXView):
    adapts(IATImage, Interface, Interface)

    def render(self):
        image = self.context.getImage()
        image_layout = IBlockConfig(self.context).image_layout
        caption = self.context.Description()
        generator = ImageLaTeXGenerator(self.context, self.layout)
        return generator(image, image_layout, floatable=False,
                         caption=caption)
