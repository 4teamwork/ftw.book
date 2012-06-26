from Acquisition import aq_inner, aq_parent
from Products.Archetypes import atapi
from Products.Archetypes import public
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from ftw.book import _
from ftw.book.interfaces import IBook
from ftw.book.latex.layouts import register_book_layout
from ftw.book.latex.utils import get_raw_image_data
from ftw.pdfgenerator.babel import get_preferred_babel_option_for_context
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from zope.component import adapts
from zope.dottedname.resolve import resolve
from zope.interface import implements, Interface


class StringField(ExtensionField, public.StringField):
    pass


class TextField(ExtensionField, public.TextField):
    pass


class FileField(ExtensionField, public.FileField):
    pass


class IntegerField(ExtensionField, public.IntegerField):
    pass


class IDefaultBookLayoutSelectionLayer(Interface):
    """Request layer interface for selecting the default book layout.
    """

register_book_layout(IDefaultBookLayoutSelectionLayer,
                     _(u'Default layout'))


class DefaultBookLayoutExtender(object):
    """Schema extender, adding the layout-specific fields "release", "author"
    and "author_address" to the book when the default layout is selected.
    """

    adapts(IBook)
    implements(ISchemaExtender)

    fields = [
        StringField(
            name='release',
            default='',
            required=False,
            widget=atapi.StringWidget(
                label=_(u'book_label_release', default=u'Release'),
                )),

        StringField(
            name='author',
            default='',
            required=False,
            widget=atapi.StringWidget(
                label=_(u'book_label_author', default=u'Author'),
                )),

        TextField(
            name='author_address',
            default='',
            required=False,
            default_content_type='text/plain',
            allowable_content_types=('text/plain',),
            default_output_type='text/plain',

            widget=atapi.TextAreaWidget(
                label=_(u'book_label_author_address',
                        default=u'Author Address'),
                        )),

        FileField(
            name='titlepage_logo',
            required=False,

            widget=atapi.FileWidget(
                label=_(u'book_label_titlepage_logo',
                        default=u'Titlepage logo'),
                description=_(u'book_help_titlepage_logo',
                              default=u'Upload an image or a PDF, which '
                              u'will be displayed on the titlepage'))),

        IntegerField(
            name='titlepage_logo_width',
            default=0,
            required=False,
            size=3,

            widget=atapi.IntegerWidget(
                label=_(u'book_label_titlepage_logo_width',
                       default=u'Titlepage logo width (%)'),
                description=_(u'book_help_titlepage_logo_width',
                              default=u'Width of the titlepage logo in '
                              u'percent of the content width.'),
                size=3,
                maxlength=3)),

        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        # Checking whether the request provides the
        # IDefaultBookLayoutSelectionLayer interface does not work when
        # LinguaPlone is installed.
        # Looks like this method is called before
        # BookTraverse.publishTraverse() marks the request with the interface.

        layout_layer_name = getattr(self.context, 'latex_layout', None)
        if layout_layer_name:
            layout_layer = resolve(layout_layer_name)
            if layout_layer == IDefaultBookLayoutSelectionLayer:
                return self.fields
        return []


class DefaultBookLayout(MakoLayoutBase):
    """A default book layout based on sphinx layout.
    """

    adapts(Interface, IDefaultBookLayoutSelectionLayer, IBuilder)

    template_directories = ['default_layout_templates']
    template_name = 'main.tex'

    def get_render_arguments(self):
        book = self.get_book()

        convert = self.get_converter().convert

        address = book.Schema().getField('author_address').get(book)
        address = convert(address.replace('\n', '<br />')).replace('\n', '')

        logo = book.Schema().getField('titlepage_logo').get(book)
        if logo and logo.data:
            logo_filename = 'titlepage_logo.jpg'
            self.get_builder().add_file(
                logo_filename,
                data=get_raw_image_data(logo.data))

            logo_width = book.Schema().getField(
                'titlepage_logo_width').get(book)
        else:
            logo_filename = False
            logo_width = 0

        args = {
            'context_is_book': self.context == book,
            'title': convert(book.Title()),
            'use_titlepage': book.getUse_titlepage(),
            'logo': logo_filename,
            'logo_width': logo_width,
            'use_toc': book.getUse_toc(),
            'use_lot': book.getUse_lot(),
            'use_loi': book.getUse_loi(),
            'release': convert(book.Schema().getField('release').get(book)),
            'author': convert(book.Schema().getField('author').get(book)),
            'authoraddress': address,
            'babel': get_preferred_babel_option_for_context(self.context),
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

        # The sphinx document class requires graphicx and hyperref, so we
        # need to remove those packages from the document, otherwise it
        # would clash.
        self.remove_package('graphicx')
        self.remove_package('hyperref')
