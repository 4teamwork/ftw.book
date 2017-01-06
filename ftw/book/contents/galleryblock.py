from ftw.book.interfaces import IBookGalleryBlock
from ftw.simplelayout.contenttypes.contents import galleryblock
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IBookGalleryBlockSchema(galleryblock.IGalleryBlockSchema):
    pass


class BookGalleryBlock(galleryblock.GalleryBlock):
    implements(IBookGalleryBlock)
