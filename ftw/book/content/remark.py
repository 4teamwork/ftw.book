from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IRemark
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.types.common.content import simplelayout_schemas
from zope.i18nmessageid import MessageFactory
from zope.interface import implements


_sl = MessageFactory('simplelayout')

remark_schema = ATContentTypeSchema.copy()

remark_schema += simplelayout_schemas.textSchema.copy()

remark_schema['title'].required = False
remark_schema['title'].searchable = 0
remark_schema['excludeFromNav'].default = True
remark_schema['description'].widget.visible = {'edit': 0, 'view': 0}
simplelayout_schemas.finalize_simplelayout_schema(remark_schema)


class Remark(ATDocumentBase):
    """A simplelayout block used for comments
    """

    security = ClassSecurityInfo()
    implements(IRemark, ISimpleLayoutBlock)
    schema = remark_schema


atapi.registerType(Remark, PROJECTNAME)
