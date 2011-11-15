from simplelayout.base.viewlets import SimpleLayoutListingViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.helpers import Numbering


class SimpleLayoutListingViewlet(SimpleLayoutListingViewlet):

    render = ViewPageTemplateFile('listing.pt')
    numbering = Numbering()

    def get_valid_parent_h_tags(self):
        return self.numbering.generate_valid_parent_h_tags(self.context)
