from ftw.book.content import textblock
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin


class HTMLBlock(ATCTContent, HistoryAwareMixin):
    schema = ATContentTypeSchema.copy() + \
        textblock.default_schema.copy()


atapi.registerType(HTMLBlock, 'ftw.book')
