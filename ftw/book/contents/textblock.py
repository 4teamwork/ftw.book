from ftw.book.interfaces import IBookTextBlock
from ftw.simplelayout.contenttypes.contents.textblock import ITextBlockSchema
from ftw.simplelayout.contenttypes.contents.textblock import TextBlock
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IBookTextBlockSchema(ITextBlockSchema):
    pass


class BookTextBlock(TextBlock):
    implements(IBookTextBlock)
