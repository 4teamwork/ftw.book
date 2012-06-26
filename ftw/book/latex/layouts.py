from ftw.book.config import BOOK_LAYOUT_REGISTRY
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


def register_book_layout(request_layer, title):
    """Registers a custom book layout, selectable in the book edit form.
    The `request_layer` interface of the select layout will be provided by
    the request when the PDF is exported. The layout adapter needs to adapt
    the `request_layer`. The `request_layer` should not be registered as
    normal browser layer.

    Arguments:
    request_layer -- a request layer interface, adapted by the layout
    title -- the title of the layout, displayed in the layout selection

    """
    dotted_name = '.'.join((request_layer.__module__, request_layer.__name__))
    BOOK_LAYOUT_REGISTRY[dotted_name] = title


class LayoutsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Returns a vocabulary with all known LaTeX layouts. A LaTeX layout
        is "registered" by subclassing IBookLaTeXLayoutSelectionLayer and
        providing an adapter, which uses the new interface as request
        discriminator.
        """
        terms = []

        for iface_dotted_name, title in BOOK_LAYOUT_REGISTRY.items():
            value = iface_dotted_name
            terms.append(SimpleVocabulary.createTerm(value, value, title))

        return SimpleVocabulary(terms)
