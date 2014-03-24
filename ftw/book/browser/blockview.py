from Products.Five.browser import BrowserView
from ftw.book.helpers import BookHelper
from ftw.contentpage.browser.textblock_view import TextBlockView


class BookTextBlockView(TextBlockView):

    def get_dynamic_title(self):
        return BookHelper()(self.context)


class HTMLBlockView(BrowserView):

    def get_dynamic_title(self):
        return BookHelper()(self.context)


class BookChapterView(BrowserView):

    def get_dynamic_title(self):
        return BookHelper()(self.context, linked=True)
