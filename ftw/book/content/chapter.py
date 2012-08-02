from AccessControl import ClassSecurityInfo
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IChapter
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISimpleLayoutCapable
from simplelayout.types.common.content.page import Page
from zope.interface import implements


class Chapter(Page):
    implements(IChapter, ISimpleLayoutCapable, ISimpleLayoutBlock)
    security = ClassSecurityInfo()

    schema = Page.schema.copy()

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


registerType(Chapter, PROJECTNAME)
