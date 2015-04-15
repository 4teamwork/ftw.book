from ftw.book.interfaces import IBook, IWithinBookLayer
from ftw.pdfgenerator.utils import provide_request_layer
from zope.component import adapts
from zope.dottedname.resolve import resolve
from zope.interface import directlyProvidedBy, directlyProvides
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse


class BookTraverse(DefaultPublishTraverse):
    adapts(IBook, IRequest)

    def publishTraverse(self, request, name):

        provideBookLayers(self.context, request)

        return super(BookTraverse, self).publishTraverse(request, name)


def provideBookLayers(context, request):
    layout_layer_name = getattr(context, 'latex_layout', '')
    if layout_layer_name:
        layout_layer = resolve(layout_layer_name)
        provide_request_layer(request, layout_layer)

    provide_request_layer(request, IWithinBookLayer)


class BookContext(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __enter__(self):
        self.original_interfaces = list(directlyProvidedBy(self.request))
        provideBookLayers(self.context, self.request)

    def __exit__(self, exc_type, exc_value, traceback):
        directlyProvides(self.request, *self.original_interfaces)
