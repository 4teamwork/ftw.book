from Products.ATContentTypes.browser import nextprevious
from ftw.book.interfaces import IBook
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from zope.component import adapts
from zope.interface import implements


class BookNextPrevious(nextprevious.ATFolderNextPrevious):
    """Let a folder act as a next/previous provider. This will be
    automatically found by the @@plone_nextprevious_view and viewlet.
    """

    implements(INextPreviousProvider)
    adapts(IBook)

    def buildNextPreviousQuery(self, *args, **kwargs):
        query = super(BookNextPrevious, self).buildNextPreviousQuery(
            *args, **kwargs)
        del query['is_folderish']
        return query
