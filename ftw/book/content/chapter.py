from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IChapter
from ftw.contentpage.content.schema import finalize
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISimpleLayoutCapable
from zope.interface import implements


try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType


chapter_schema = folder.ATFolder.schema.copy()
finalize(chapter_schema, hide=['description'])
chapter_schema['excludeFromNav'].default = False


class Chapter(folder.ATFolder):
    implements(IChapter, ISimpleLayoutCapable, ISimpleLayoutBlock)
    security = ClassSecurityInfo()

    schema = chapter_schema

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


registerType(Chapter, PROJECTNAME)
