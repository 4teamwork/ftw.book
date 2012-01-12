from Acquisition import aq_inner, aq_parent
from ftw.book import _
from ftw.book.config import BOOK_LAYOUT_REGISTRY
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IWithinBookLayer
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from zope.component import adapts
from zope.interface import implements, Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


def register_book_layout(request_layer, title):
    """Registers a custom book layout, selectable in the book edit form.
    The `request_layer` interface of the select layout will be provided by
    the requst when the PDF is exported. The layout adapter needs to adapt
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
        """Returns a vocubulary with all known LaTeX layouts. A LaTeX layout
        is "registered" by subclassing IBookLaTeXLayoutSelectionLayer and
        providing an adapter, which uses the new interface as request
        descriminator.
        """
        terms = []

        for iface_dotted_name, title in BOOK_LAYOUT_REGISTRY.items():
            value = iface_dotted_name
            terms.append(SimpleVocabulary.createTerm(value, value, title))

        return SimpleVocabulary(terms)


class IDefaultBookLayoutSelectionLayer(IWithinBookLayer):
    """Request layer interface for selecting the default book layout.
    """

register_book_layout(IDefaultBookLayoutSelectionLayer,
                     _(u'Default layout'))


class DefaultBookLayout(MakoLayoutBase):
    """A default book layout based on sphinx layout.
    """

    adapts(Interface, IDefaultBookLayoutSelectionLayer, IBuilder)

    template_directories = ['default_layout_templates']
    template_name = 'main.tex'

    def get_render_arguments(self):
        book = self.get_book()

        convert = self.get_converter().convert

        address = book.getAuthor_address().replace('\n', '<br />')
        address = convert(address).replace('\n', '')

        args = {
            'context_is_book': self.context == book,
            'title': convert(book.Title()),
            'use_titlepage': book.getUse_titlepage(),
            'use_toc': book.getUse_toc(),
            'use_lot': book.getUse_lot(),
            'use_loi': book.getUse_loi(),
            'release': convert(book.getRelease()),
            'author': convert(book.getAuthor()),
            'authoraddress': address,
            # XXX: how to use in this layout?
            # 'pagestyle': book.getPagestyle(),
            }
        return args

    def get_book(self):
        obj = self.context
        while obj and not IBook.providedBy(obj):
            obj = aq_parent(aq_inner(obj))
        return obj

    def before_render_hook(self):
        self.use_package('inputenc', options='utf8', append_options=False)
        self.use_package('fontenc', options='T1', append_options=False)
        self.use_package('babel')
        self.use_package('times')
        self.use_package('fncychap', 'Sonny', append_options=False)
        self.use_package('longtable')
        self.use_package('sphinx')

        self.add_raw_template_file('sphinx.sty')
        self.add_raw_template_file('fncychap.sty')
        self.add_raw_template_file('sphinxftw.cls')
        self.add_raw_template_file('sphinxhowto.cls')
        self.add_raw_template_file('sphinxmanual.cls')
