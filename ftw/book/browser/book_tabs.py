from ftw.book.browser.index_view import IndexView
from ftw.tabbedview.browser.listing import CatalogListingView
from ftw.book import _
from ftw.table import helper


class IndexTab(IndexView):
    """Index Tab (for tabbed_view)"""

    def get_css_classes(self):
        return ['searchform-hidden']


class DocumentsTab(CatalogListingView):

    types = ['ftw.file.File', 'Image']
    sort_on = 'created'
    show_selects = False
    show_menu = False

    columns = ({'column': 'Title',
                'column_title': _(u'column_title', default=u'Title'),
                'sort_index': 'sortable_title',
                'transform': helper.linked},
               {'column': 'documentDate',
                'column_title': _(u'column_date', default=u'date'),
                'transform': helper.readable_date},
               {'column': 'Creator',
                'column_title': _(u'column_creator', default=u'Creator'),
                'sort_index': 'sortable_creator',
                'transform': helper.readable_author},
               {'column': 'modified',
                'column_title': _(u'column_modified', default=u'modified'),
                'transform': helper.readable_date},
               )
