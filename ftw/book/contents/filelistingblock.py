from ftw.book.interfaces import IBookFileListingBlock
from ftw.simplelayout.contenttypes.contents import filelistingblock
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IBookFileListingBlockSchema(filelistingblock.IFileListingBlockSchema):
    pass


class BookFileListingBlock(filelistingblock.FileListingBlock):
    implements(IBookFileListingBlock)
