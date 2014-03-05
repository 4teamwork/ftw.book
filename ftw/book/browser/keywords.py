from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class KeywordsTab(BrowserView):

    template = ViewPageTemplateFile('keywords.pt')

    def __call__(self):
        return self.template()
