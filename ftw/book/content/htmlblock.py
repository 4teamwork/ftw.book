from AccessControl import ClassSecurityInfo
from Products.ATContentTypes import ATCTMessageFactory as _at
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IHTMLBlock
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.types.common.content import simplelayout_schemas
from zope.i18nmessageid import MessageFactory
from zope.interface import implements


_sl = MessageFactory('simplelayout')


htmlblock_schema = ATContentTypeSchema.copy()

htmlblock_schema += atapi.Schema((

        atapi.BooleanField(
            name='showTitle',
            schemata='default',
            default=False,

            widget=atapi.BooleanWidget(
                label=_sl(u'simplelayout_label_showtitle',
                          default=u'Show Title'),
                description=_sl(u'simplelayout_help_showtitle',
                                default=u'Show title'))),

        ))

htmlblock_schema += simplelayout_schemas.textSchema.copy()

htmlblock_schema['text'].widget = atapi.TextAreaWidget(
    label=_at(u'label_body_text', default=u'Body Text'),
    description='',
    rows=32,
    cols=70)

htmlblock_schema['title'].required = False
htmlblock_schema['title'].searchable = 0
htmlblock_schema['excludeFromNav'].default = True
htmlblock_schema['description'].widget.visible = {'edit': 0, 'view': 0}
simplelayout_schemas.finalize_simplelayout_schema(htmlblock_schema)


class HTMLBlock(ATDocumentBase):
    """A simplelayout block providing an HTML text field.
    """

    security = ClassSecurityInfo()
    implements(IHTMLBlock, ISimpleLayoutBlock)
    schema = htmlblock_schema


atapi.registerType(HTMLBlock, PROJECTNAME)
