from simplelayout.types.common.browser.views import BlockView
from ftw.book.helpers import BookHelper


class BlockView(BlockView):

    helper = BookHelper()

    def get_dynamic_title(self):
        return self.helper(self.context)