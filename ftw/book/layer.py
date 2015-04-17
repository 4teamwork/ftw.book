from contextlib import contextmanager
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IWithinBookLayer
from ftw.pdfgenerator.utils import provide_request_layer
from zope.component import adapts
from zope.dottedname.resolve import resolve
from zope.interface import directlyProvidedBy, directlyProvides
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse


class BookTraverse(DefaultPublishTraverse):
    adapts(IBook, IRequest)

    def publishTraverse(self, request, name):
        provide_book_layers(self.context, request)
        return super(BookTraverse, self).publishTraverse(request, name)


def provide_book_layers(book, request):
    layout_layer_name = getattr(book, 'latex_layout', '')
    if layout_layer_name:
        layout_layer = resolve(layout_layer_name)
        provide_request_layer(request, layout_layer)
    provide_request_layer(request, IWithinBookLayer)


@contextmanager
def providing_book_layers(book, request):
    original_interfaces = list(directlyProvidedBy(request))
    provide_book_layers(book, request)
    try:
        yield
    finally:
        directlyProvides(request, *original_interfaces)
