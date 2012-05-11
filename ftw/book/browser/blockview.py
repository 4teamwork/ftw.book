from ftw.book.helpers import BookHelper
from simplelayout.types.common.browser.views import BlockView


class BookBlockView(BlockView):

    def get_dynamic_title(self):
        return BookHelper()(self.context)


class BookChapterView(BlockView):

    def get_dynamic_title(self):
        return BookHelper()(self.context, linked=True)
