from ftw.book.contents.filelistingblock import IBookFileListingBlock
from ftw.book.helpers import BookHelper
from ftw.simplelayout.contenttypes.browser import filelistingblock
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BookFileListingBlockView(filelistingblock.FileListingBlockView):
    template = ViewPageTemplateFile('templates/listingblock.pt')

    @property
    def title_html(self):
        if not IBookFileListingBlock(self.context).show_title:
            return ''
        return BookHelper()(self.context)
