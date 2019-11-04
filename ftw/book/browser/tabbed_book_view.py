from ftw.book import _
from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper


class BooksView(TabbedView):

    def get_tabs(self):
        return [{'id': 'books', 'class': ''}, ]


class Tab(CatalogListingView):

    def __init__(self, *args, **kwargs):
        super(Tab, self).__init__(*args, **kwargs)
        self.filter_path = ''

    def update_config(self):
        super(Tab, self).update_config()
        self.filter_path = '/'.join(
            self.context.portal_url.getPortalObject().getPhysicalPath())


class BooksTab(Tab):

    types = 'Book'
    sort_on = 'sortable_title'
    show_selects = False
    show_menu = False

    columns = (
        {'column': 'Title',
         'column_title': _(u'column_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': helper.linked},
        {'column': 'Creator',
         'column_title': _(u'column_creator', default=u'Creator'),
         'sort_index': 'sortable_creator',
         'transform': helper.readable_author}, )
