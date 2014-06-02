from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IRemark
from ftw.contentpage.content import textblock
from ftw.contentpage.content.schema import finalize
from zope.interface import implements


try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi


remark_schema = ATContentTypeSchema.copy() + \
    textblock.default_schema.copy()
remark_schema['title'].required = False
remark_schema['title'].searchable = 0
finalize(remark_schema, hide=['description', 'showTitle'])


class Remark(textblock.TextBlock):
    """A simplelayout block used for comments
    """

    security = ClassSecurityInfo()
    implements(IRemark)
    schema = remark_schema


atapi.registerType(Remark, PROJECTNAME)
