from ZPublisher.BaseRequest import DefaultPublishTraverse
from ftw.book.interfaces import IBook, IWithinBookLayer
from zope.component import adapts
from zope.dottedname.resolve import resolve
from ftw.pdfgenerator.utils import provide_request_layer
from zope.publisher.interfaces import IRequest


class BookTraverse(DefaultPublishTraverse):
    adapts(IBook, IRequest)

    def publishTraverse(self, request, name):

        layout_layer_name = getattr(self.context, 'latex_layout', '')
        if layout_layer_name:
            layout_layer = resolve(layout_layer_name)
            provide_request_layer(request, layout_layer)

        provide_request_layer(request, IWithinBookLayer)

        return super(BookTraverse, self).publishTraverse(request, name)
