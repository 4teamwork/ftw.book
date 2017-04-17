from ftw.book.toc import TableOfContents
from ftw.htmlblock.browser.htmlblock import HtmlBlockView
from ftw.simplelayout.contenttypes.browser import filelistingblock
from ftw.simplelayout.contenttypes.browser.textblock import TextBlockView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BookChapterView(BrowserView):

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context, linked=True)


class BookTextBlockView(TextBlockView):
    template = ViewPageTemplateFile('templates/textblock.pt')
    teaser_url = None

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context)


class HTMLBlockView(HtmlBlockView):

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context)


class BookFileListingBlockView(filelistingblock.FileListingBlockView):
    template = ViewPageTemplateFile('templates/listingblock.pt')

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context)
