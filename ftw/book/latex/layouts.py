from Acquisition import aq_chain
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IBookContentType
from ftw.book.interfaces import IBookLayoutBehavior
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import logging


LOG = logging.getLogger('ftw.book.latex.layouts')


def enumerate_book_layout_behaviors():
    for name, registration in getUtilitiesFor(IBehavior):
        if IBookLayoutBehavior.providedBy(registration.interface):
            yield name, registration


def get_layout_behavior_registration(book):
    selected_registration = None
    selected_name = book.latex_layout

    for name, registration in enumerate_book_layout_behaviors():
        if name == selected_name:
            selected_registration = registration
            if not registration.marker.providedBy(book):
                alsoProvides(book, registration.marker)

        else:
            if registration.marker.providedBy(book):
                noLongerProvides(book, registration.marker)

    if not selected_registration:
        raise ValueError('No such IBookLayoutBehavior {!r}'.format(
            book.latex_layout))

    return selected_registration


@implementer(IVocabularyFactory)
class LayoutsVocabulary(object):

    def __call__(self, context):
        """Returns a vocabulary with all known LaTeX layouts. A LaTeX layout
        is "registered" by subclassing IBookLaTeXLayoutSelectionLayer and
        providing an adapter, which uses the new interface as request
        discriminator.
        """
        terms = []

        for name, registration in enumerate_book_layout_behaviors():
            title = registration.title
            terms.append(SimpleVocabulary.createTerm(name, name, title))

        return SimpleVocabulary(terms)


@adapter(IBook)
class BookBehaviorAssignable(DexterityBehaviorAssignable):
    """Custom behavior assignable for books, allowing to also activate
    the selected layout behavior.
    """

    def __init__(self, context):
        super(BookBehaviorAssignable, self).__init__(context)
        self.book = context

    def enumerateBehaviors(self):
        for behavior in super(BookBehaviorAssignable,
                              self).enumerateBehaviors():
            yield behavior

        try:
            yield get_layout_behavior_registration(self.book)
        except ValueError, exc:
            LOG.exception(exc)


@adapter(IBookContentType, Interface, IBuilder)
@implementer(ILaTeXLayout)
def inherit_book_layout(context, request, builder):
    books = filter(IBook.providedBy, aq_chain(context))
    if not books:
        return None

    layout = getMultiAdapter((books[0], request, builder), ILaTeXLayout)
    # Since the layout has the book as context, we've lost track of on which
    # context the export was started (export_context).
    # This is only relevant for fixing chapter counters book internally.
    # We just set the export_context here in order to be able to fix
    # the chapter counters later.
    setattr(layout, 'export_context', context)
    return layout
