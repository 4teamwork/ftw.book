from ZPublisher.BaseRequest import DefaultPublishTraverse
from ftw.book.interfaces import IBook, IWithinBookLayer
from zope.component import adapts
from zope.dottedname.resolve import resolve
from zope.interface import directlyProvidedBy, directlyProvides
from zope.publisher.interfaces import IRequest


class BookTraverse(DefaultPublishTraverse):
    adapts(IBook, IRequest)

    def publishTraverse(self, request, name):
        provide_layers = []

        layout_layer_name = getattr(self.context, 'latex_layout', '')
        layout_layer = resolve(layout_layer_name)
        if not layout_layer.providedBy(request):
            provide_layers.append(layout_layer)

        if not IWithinBookLayer.providedBy(request):
            provide_layers.append(IWithinBookLayer)

        if provide_layers:
            ifaces = provide_layers + list(directlyProvidedBy(request))

            # Since we allow multiple markers here, we can't use
            # zope.publisher.browser.applySkin() since this filters out
            # IBrowserSkinType interfaces, nor can we use alsoProvides(), since
            # this appends the interface (in which case we end up *after* the
            # default Plone/CMF skin)
            directlyProvides(request, *ifaces)

        return super(BookTraverse, self).publishTraverse(request, name)
