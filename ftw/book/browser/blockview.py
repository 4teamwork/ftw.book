from ftw.book.toc import TableOfContents
from ftw.htmlblock.browser.htmlblock import HtmlBlockView
from ftw.simplelayout.contenttypes.browser.filelistingblock import FileListingBlockView
from ftw.simplelayout.contenttypes.browser.galleryblock import GalleryBlockView
from ftw.simplelayout.contenttypes.browser.textblock import TextBlockView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BookBlockMixin:
    book_template = ViewPageTemplateFile('templates/titled_block_view.pt')

    def __call__(self):
        return self.book_template()

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context, linked=False)


class BookChapterView(BrowserView):

    @property
    def block_title(self):
        return TableOfContents().html_heading(self.context, linked=True)


class BookTextBlockView(BookBlockMixin, TextBlockView):
    teaser_url = None


class BookFileListingBlockView(BookBlockMixin, FileListingBlockView):
    pass


class BookGalleryBlockView(BookBlockMixin, GalleryBlockView):
    pass


class HTMLBlockView(BookBlockMixin, HtmlBlockView):
    pass
