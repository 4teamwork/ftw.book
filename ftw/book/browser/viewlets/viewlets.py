from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.helpers import BookHelper
from simplelayout.base import viewlets


class SimpleLayoutListingViewlet(viewlets.SimpleLayoutListingViewlet):

    render = ViewPageTemplateFile('listing.pt')
    helper = BookHelper()

    def get_valid_parent_h_tags(self):
        return self.helper.generate_valid_hierarchy_h_tags(self.context)
