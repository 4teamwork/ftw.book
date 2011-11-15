from simplelayout.types.common.browser.views import BlockView
from ftw.book.helpers import Numbering


class BlockView(BlockView):

    numbering = Numbering()

    def get_dynamic_title(self):
        return self.numbering(self.context)