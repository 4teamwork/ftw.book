from Products.Archetypes import atapi
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextField
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from ftw.book import _
from ftw.book.interfaces import IChapter
from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.interfaces import ModifyLaTeXInjection
from ftw.book.interfaces import NO_PREFERRED_LAYOUT
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.component import adapts
from zope.interface import implements
import sys


class LaTeXCodeField(ExtensionField, TextField):
    pass


class ExtensionStringField(ExtensionField, StringField):
    pass


class ExtensionBooleanField(ExtensionField, BooleanField):
    pass


def add_field(field, condition=None, interfaces=None, insert_after=None):
    """Add a field under certain conditions.

    Arguments:

    field -- The schema extender field (subclassing ExtensionField)

    condition -- A function - called with context as argument - for deciding
    whether to inject the field or not.

    interfaces -- A list of interfaces from which at least one has to be
    provided by the context for the field to be applied.

    insert_after -- A string fieldname, after which this field is
    positioned, if both fields are in the same schemata.
    """

    cls = sys._getframe(1).f_locals
    cls['_fields'].append({'field': field,
                           'condition': condition,
                           'interfaces': interfaces,
                           'insert_after': insert_after})


class LaTeXCodeInjectionExtender(object):
    adapts(ILaTeXCodeInjectionEnabled)
    implements(IOrderableSchemaExtender)

    _fields = []

    add_field(LaTeXCodeField(
            name='preLatexCode',
            schemata='LaTeX',
            default_content_type='application/x-latex',
            allowable_content_types='application/x-latex',
            write_permission=ModifyLaTeXInjection,

            widget=atapi.TextAreaWidget(
                label=_(u'pre_latex_code_label',
                        default=u'LaTeX code above content'),
                description=_(u'pre_latex_code_help',
                              default=u''))))

    add_field(LaTeXCodeField(
            name='postLatexCode',
            schemata='LaTeX',
            default_content_type='application/x-latex',
            allowable_content_types='application/x-latex',
            write_permission=ModifyLaTeXInjection,

            widget=atapi.TextAreaWidget(
                label=_(u'post_latex_code_label',
                        default=u'LaTeX code beneath content'),
                description=_(u'post_latex_code_help',
                              default=u''))))

    add_field(ExtensionStringField(
            name='preferredColumnLayout',
            schemata='LaTeX',
            default=NO_PREFERRED_LAYOUT,
            write_permission=ModifyLaTeXInjection,
            vocabulary=((NO_PREFERRED_LAYOUT,
                         _('injection_label_no_preferred_column_layout',
                           default='No preferred column layout')),

                        (ONECOLUMN_LAYOUT,
                         _('injection_label_one_column_layout',
                           default='One column layout')),

                        (TWOCOLUMN_LAYOUT,
                         _('injection_label_two_column_layout',
                           default='Two column layout'))),

            widget=atapi.SelectionWidget(
                label=_(u'injection_label_preferred_column_layout',
                        default=u'Preferred layout'),
                description=_(
                    u'injection_help_preferred_column_layout',
                    default=u'When choosing a one or two column layout, the '
                    u'layout will switched for this content and all '
                    u'subsequent contents in the PDF, if necessary. '
                    u'If "no preferred layout" is selected the currently '
                    u'active layout is kept.'))))

    add_field(
        interfaces=[IChapter, ISimpleLayoutBlock],
        field=ExtensionBooleanField(
            name='latexLandscape',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_landscape',
                        default=u'Use landscape'))))

    add_field(
        interfaces=[IChapter, ISimpleLayoutBlock],
        field=ExtensionBooleanField(
            name='preLatexClearpage',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_insert_clearpage_before_content',
                        default=u'Insert page break before this content'))))

    add_field(
        interfaces=[IChapter, ISimpleLayoutBlock],
        field=ExtensionBooleanField(
            name='postLatexClearpage',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_insert_clearpage_after_content',
                        default=u'Insert page break after this content'))))

    add_field(
        interfaces=[IChapter, ISimpleLayoutBlock],
        field=ExtensionBooleanField(
            name='preLatexNewpage',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_insert_newpage_before_content',
                        default=u'Insert column break before this content'),
                description=_(u'This option inserts a column break when '
                              u'two column layout is active.'))))

    add_field(
        # hideFromTOC is only useful when we have a showTitle checkbox too
        condition=lambda context: context.schema.get('showTitle'),
        insert_after='showTitle',
        field=ExtensionBooleanField(
            name='hideFromTOC',
            default=False,
            required=False,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_hide_from_toc',
                        default=u'Hide from table of contents'),
                description=_(u'injection_help_hide_from_toc',
                              default=u'Hides the title from the table of '
                              u'contents and does not number the heading.'))))

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if not self._context_is_within_book():
            return []

        fields = []

        for item in self._fields:
            condition = item.get('condition')
            if condition and not condition(self.context):
                continue

            interfaces = item.get('interfaces')
            if interfaces:
                provided = [iface for iface in interfaces
                            if iface.providedBy(self.context)]
                if len(provided) == 0:
                    continue

            fields.append(item.get('field'))

        return fields

    def getOrder(self, schematas):
        for item in self._fields:
            insert_after = item.get('insert_after')
            if not insert_after:
                continue

            field = item.get('field')
            if field.schemata not in schematas:
                continue

            schemata = schematas[field.schemata]
            if insert_after not in schemata or field.__name__ not in schemata:
                continue

            schemata.remove(field.__name__)
            schemata.insert(schemata.index(insert_after) + 1, field.__name__)

        return schematas

    def _context_is_within_book(self):
        # In some cases REQUEST is no available.
        if not hasattr(self.context, 'REQUEST'):
            return False

        if IWithinBookLayer.providedBy(self.context.REQUEST):
            return True
        return False
