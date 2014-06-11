from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from ftw.book import _
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IHTMLBlock
from ftw.contentpage.content import textblock
from ftw.contentpage.content.schema import finalize
from zope.interface import implements


if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi


htmlblock_schema = ATContentTypeSchema.copy() + \
    textblock.default_schema.copy()

htmlblock_schema['title'].required = False
htmlblock_schema['description'].widget.visible = {'view': 'invisible',
                                                  'edit': 'invisible'}

htmlblock_schema['text'].validators = ()
htmlblock_schema['text'].default_output_type = 'text/html'
htmlblock_schema['text'].widget = atapi.TextAreaWidget(
    label=_(u'label_html', default=u'HTML'),
    description='',
    rows=32,
    cols=70)

finalize(htmlblock_schema)


class HTMLBlock(textblock.TextBlock):
    """HTML block for books.
    """

    security = ClassSecurityInfo()
    implements(IHTMLBlock)
    schema = htmlblock_schema


atapi.registerType(HTMLBlock, PROJECTNAME)
