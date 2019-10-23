from Acquisition import aq_chain
from ftw.book import _
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IBookLayoutBehavior
from ftw.pdfgenerator.babel import get_preferred_babel_option_for_context
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel.model import Schema
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Int
from zope.schema import Text
from zope.schema import TextLine


# AT -> DX migration hints.
OLD_AT_INTERFACE = 'ftw.book.latex.defaultlayout.IDefaultBookLayoutSelectionLayer'
OLD_FIELDNAMES = ('release', 'author', 'author_address', 'titlepage_logo', 'titlepage_logo_width')
OLD_NEW_MAPPING = {'author': 'book_author'}


@provider(IFormFieldProvider, IBookLayoutBehavior)
class IDefaultBookLayout(Schema):
    """Book instance behavior for a standard book layout.
    """

    release = TextLine(
        title=_(u'book_label_release', default=u'Release'),
        required=False,
        default=u'')

    book_author = TextLine(
        title=_(u'book_label_author', default=u'Author'),
        required=False,
        default=u'')

    author_address = Text(
        title=_(u'book_label_author_address', default=u'Author Address'),
        required=False,
        default=u'')

    titlepage_logo = NamedBlobImage(
        title=_(u'book_label_titlepage_logo', default=u'Titlepage logo'),
        description=_(u'book_help_titlepage_logo',
                      default=u'Upload an image or a PDF, which '
                      u'will be displayed on the titlepage'),
        required=False)

    titlepage_logo_width = Int(
        title=_(u'book_label_titlepage_logo_width',
                default=u'Titlepage logo width (%)'),
        description=_(u'book_help_titlepage_logo_width',
                      default=u'Width of the titlepage logo in '
                      u'percent of the content width.'),
        max=3,
        required=False,
        default=0)


class IDefaultBookLayoutEnabled(Interface):
    """Marker interface for default book layout behavior.
    """


@adapter(IDefaultBookLayoutEnabled, Interface, IBuilder)
@implementer(ILaTeXLayout)
class DefaultBookLayout(MakoLayoutBase):

    template_directories = ['default_layout_templates']
    template_name = 'main.tex'

    def get_render_arguments(self):
        book = self.get_book()
        convert = self.get_converter().convert

        address = IDefaultBookLayout(book).author_address or u''
        if address:
            transforms = getToolByName(self.context, 'portal_transforms')
            address = transforms('text_to_html',
                                 address.encode('utf-8')).decode('utf-8')

        logo = IDefaultBookLayout(book).titlepage_logo
        if logo and logo.size:
            logo_filename = 'titlepage_logo.jpg'
            with logo.open() as logofio:
                self.get_builder().add_file(
                    logo_filename, logofio)
            logo_width = IDefaultBookLayout(book).titlepage_logo_width
        else:
            logo_filename = False
            logo_width = 0

        export_context = getattr(self, 'export_context', self.context)
        args = {
            'context_is_book': export_context == book,
            'title': book.Title(),
            'use_titlepage': book.use_titlepage,
            'logo': logo_filename,
            'logo_width': logo_width,
            'use_toc': book.use_toc,
            'use_lot': book.use_lot,
            'use_loi': book.use_loi,
            'use_index': book.use_index,
            'release': convert(IDefaultBookLayout(book).release or u''),
            'author': convert(IDefaultBookLayout(book).book_author or u''),
            'authoraddress': convert(address),
            'babel': get_preferred_babel_option_for_context(self.context),
            'index_title': self.get_index_title(),
        }
        return args

    def get_book(self):
        return filter(IBook.providedBy, aq_chain(self.context))[0]

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
        self.add_raw_template_file('tabulary.sty')
        self.add_raw_template_file('sphinxftw.cls')
        self.add_raw_template_file('sphinxhowto.cls')
        self.add_raw_template_file('sphinxmanual.cls')

        # The sphinx document class requires graphicx and hyperref, so we
        # need to remove those packages from the document, otherwise it
        # would clash.
        self.remove_package('graphicx')
        self.remove_package('hyperref')

    def get_index_title(self):
        context_language_method = getattr(self.context, 'getLanguage', None)
        if context_language_method:
            language_code = context_language_method()

        else:
            ltool = getToolByName(self.context, 'portal_languages')
            language_code = ltool.getPreferredLanguage()

        return translate(_(u'title_index', default=u'Index'),
                         target_language=language_code)
