from ftw.book.contents.htmlblock import IBookHtmlBlockSchema
from ftw.book.contents.textblock import IBookTextBlockSchema
from ftw.book.helpers import BookHelper
from ftw.htmlblock.browser.htmlblock import HtmlBlockView
from ftw.simplelayout.contenttypes.browser.textblock import TextBlockView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BookTextBlockView(TextBlockView):
    template = ViewPageTemplateFile('templates/textblock.pt')
    teaser_url = None

    @property
    def block_title(self):
        if not IBookTextBlockSchema(self.context).show_title:
            return ''
        return BookHelper()(self.context)


class HTMLBlockView(HtmlBlockView):

    @property
    def block_title(self):
        if not IBookHtmlBlockSchema(self.context).show_title:
            return ''
        return BookHelper()(self.context)


class BookChapterView(BrowserView):

    def get_dynamic_title(self):
        return BookHelper()(self.context, linked=True)
