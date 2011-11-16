from simplelayout.base.viewlets import SimpleLayoutListingViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.helpers import BookHelper


class SimpleLayoutListingViewlet(SimpleLayoutListingViewlet):

    render = ViewPageTemplateFile('listing.pt')
    helper = BookHelper()

    def get_valid_parent_h_tags(self):
        return self.helper.generate_valid_parent_h_tags(self.context)
