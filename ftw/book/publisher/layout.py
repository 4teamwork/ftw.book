from AccessControl.SecurityInfo import ClassSecurityInformation
from Acquisition import aq_inner
from Acquisition import aq_parent
from archetypes.schemaextender.extender import CACHE_KEY
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IWithinBookLayer
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from Products.CMFCore.interfaces import ISiteRoot
from zope.dottedname.resolve import resolve
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import implements


def dottedname(iface):
    """Returns the dottedname of an interface as string.
    """
    return '.'.join((iface.__module__, iface.__name__))


class BookLayoutRequestLayerCollector(object):
    """IDataCollector for supporting publishing books (ftw.publisher) with
    custom layouts and schema extender fields bound on layout request layer.

    When a custom layout is activated in the book, the request provides the
    layout interface as soon as traversing the book.
    The layout may add schema extender fields when the request provides the
    layout interface.
    In order to publish those field values correctly (with the standard
    FieldData collector), we need to provide the request layer before
    extracting data (sender) or setting data (receiver).

    Schema extender fields may be applied to not only the book itself but also
    to any content within the book. Therfore this collector should be used
    for all objects.

    The collector may be triggered when the book is traversed but also when
    it wasn't, therefore we cannot rely on the default book traversal adapter
    applying the layer interfaces to the request.
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, context):
        self.context = context

    security.declarePrivate('getData')
    def getData(self):
        book = self.get_parent_book()
        if not book:
            return None

        layers = [IWithinBookLayer]
        layout_layer_name = getattr(book, 'latex_layout', '')
        if layout_layer_name:
            layers.append(resolve(layout_layer_name))

        self.provide_request_layers(layers)
        self.flush_schemaextender_cache()
        return map(dottedname, layers)

    security.declarePrivate('setData')
    def setData(self, layers_dottednames, metadata):
        if not layers_dottednames:
            return

        self.logger.info(
            'BookLayoutRequestLayerCollector: provide request layers {0}'.format(
                layers_dottednames))

        layers = map(resolve, layers_dottednames)
        self.provide_request_layers(layers)
        self.flush_schemaextender_cache()

    def get_parent_book(self):
        context = self.context

        while context and not ISiteRoot.providedBy(context):
            if IBook.providedBy(context):
                return context
            context = aq_parent(aq_inner(context))

        return None

    def provide_request_layers(self, layers):
        """ Add a layer interface on the request
        """
        request = self.context.REQUEST
        layers = [iface for iface in layers if not iface.providedBy(request)]
        ifaces = layers + list(directlyProvidedBy(request))

        # Since we allow multiple markers here, we can't use
        # zope.publisher.browser.applySkin() since this filters out
        # IBrowserSkinType interfaces, nor can we use alsoProvides(), since
        # this appends the interface (in which case we end up *after* the
        # default Plone/CMF skin)
        directlyProvides(request, *ifaces)

    def flush_schemaextender_cache(self):
        """Flushes the schemaextender cache after conditions for
        schema extenders may have changed.
        """
        try:
            delattr(self.context.REQUEST, CACHE_KEY)
        except AttributeError:
            pass
