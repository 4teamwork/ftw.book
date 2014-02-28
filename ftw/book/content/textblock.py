from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IBookTextBlock
from ftw.contentpage.content import textblock
from zope.interface import implements


if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi


textblock_schema = textblock.textblock_schema.copy()


class BookTextBlock(textblock.TextBlock):
    """Textblock for books.
    """

    security = ClassSecurityInfo()
    implements(IBookTextBlock)
    schema = textblock_schema


atapi.registerType(BookTextBlock, PROJECTNAME)
