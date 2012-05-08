from ftw.book.helpers import BookHelper
from simplelayout.types.common.browser.views import BlockView


class BookBlockView(BlockView):

    helper = BookHelper()

    def get_dynamic_title(self):
        return self.helper(self.context)
