from zope.publisher.browser import BrowserView


class BookView(BrowserView):

    def renderindex(self):
        return self.context.restrictedTraverse('@@index_view')()
