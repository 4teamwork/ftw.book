from ZPublisher.BaseRequest import DefaultPublishTraverse
from ftw.book.interfaces import IBook, IWithinBookLayer
from zope.component import adapts
from zope.interface import directlyProvidedBy, directlyProvides
from zope.publisher.interfaces import IRequest


class BookTraverse(DefaultPublishTraverse):
    adapts(IBook, IRequest)

    def publishTraverse(self, request, name):
        if not IWithinBookLayer.providedBy(self.context):
            ifaces = [IWithinBookLayer,] + list(directlyProvidedBy(request))

            # Since we allow multiple markers here, we can't use
            # zope.publisher.browser.applySkin() since this filters out
            # IBrowserSkinType interfaces, nor can we use alsoProvides(), since
            # this appends the interface (in which case we end up *after* the
            # default Plone/CMF skin)
            directlyProvides(request, *ifaces)

        return super(BookTraverse, self).publishTraverse(request, name)
