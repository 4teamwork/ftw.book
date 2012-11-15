from Products.Archetypes import atapi
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextField
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from ftw.book import _
from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.interfaces import ModifyLaTeXInjection
from ftw.book.interfaces import NO_PREFERRED_LAYOUT
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISimpleLayoutCapable
from zope.component import adapts
from zope.interface import implements


class LaTeXCodeField(ExtensionField, TextField):
    pass


class ExtensionStringField(ExtensionField, StringField):
    pass


class ExtensionBooleanField(ExtensionField, BooleanField):
    pass


class LaTeXCodeInjectionExtender(object):
    adapts(ILaTeXCodeInjectionEnabled)
    implements(IOrderableSchemaExtender)

    fields = []

    fields.append(LaTeXCodeField(
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

    fields.append(LaTeXCodeField(
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

    fields.append(ExtensionStringField(
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

    fields.append(ExtensionBooleanField(
            name='preLatexClearpage',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_insert_clearpage_before_content',
                        default=u'Insert page break before this content'))))

    fields.append(ExtensionBooleanField(
            name='postLatexClearpage',
            schemata='LaTeX',
            default=False,
            write_permission=ModifyLaTeXInjection,

            widget=atapi.BooleanWidget(
                label=_(u'injection_label_insert_clearpage_after_content',
                        default=u'Insert page break after this content'))))

    hide_from_toc_field = ExtensionBooleanField(
        name='hideFromTOC',
        default=False,
        required=False,

        widget=atapi.BooleanWidget(
            label=_(u'injection_label_hide_from_toc',
                    default=u'Hide from table of contents'),
            description=_(u'injection_help_hide_from_toc',
                          default=u'Hides the title from the table of '
                          u'contents and does not number the heading.')))

    block_fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if not self._context_is_within_book():
            return []

        fields = self.fields[:]

        if self._is_block():
            fields.extend(self.block_fields)

            if self.context.schema.get('showTitle'):
                fields.append(self.hide_from_toc_field)

        return fields

    def getOrder(self, schematas):
        if 'default' in schematas:
            default = schematas['default']
            if 'hideFromTOC' in default and 'showTitle' in default:
                # insert hideFromTOC after showTitle
                default.remove('hideFromTOC')
                default.insert(default.index('showTitle') + 1, 'hideFromTOC')

        return schematas

    def _is_block(self):
        if not ISimpleLayoutBlock.providedBy(self.context):
            return False

        elif ISimpleLayoutCapable.providedBy(self.context):
            # We have a chapter, which is also a kind of block but in
            # this case should not match.
            return False

        else:
            return True

    def _context_is_within_book(self):

        # In some cases REQUEST is no available.
        # XXX: This is a quick fix without debugging, just a guess
        if not hasattr(self.context, 'REQUEST'):
            return False

        if IWithinBookLayer.providedBy(self.context.REQUEST):
            return True
        return False
