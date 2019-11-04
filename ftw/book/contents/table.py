from collections import OrderedDict
from collective.dexteritytextindexer import searchable
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from ftw.book import _
from ftw.book.interfaces import ITable
from ftw.book.table.generator import TableGenerator
from ftw.simplelayout.browser.actions import DefaultActions
from plone.app.textfield import RichText
from plone.autoform.directives import mode
from plone.autoform.directives import widget
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives.form import fieldset
from plone.directives.form import Schema
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Int
from zope.schema import List
from zope.schema import TextLine
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


MAX_AMOUNT_OF_COLUMNS = 12
DEFAULT_ACTIVE_COLUMNS = 3


ROW_FORMAT_VOCABULARY = SimpleVocabulary((
    SimpleTerm(value=u'', title=_(u'Normal')),
    SimpleTerm(value=u'bold', title=_(u'Bold')),
    SimpleTerm(value=u'grey', title=_(u'Grey font')),

    SimpleTerm(value=u'indent2', title=_(u'2mm indent')),
    SimpleTerm(value=u'indent10', title=_(u'10mm indent')),
    SimpleTerm(value=u'indent2 bold', title=_(u'2mm ind. + bold')),
    SimpleTerm(value=u'indent10 bold', title=_(u'10mm ind. + bold')),
    SimpleTerm(value=u'indent2 grey', title=_(u'2mm ind. + grey font')),
    SimpleTerm(value=u'indent10 grey', title=_(u'10mm ind. + grey font')),

    SimpleTerm(value=u'noborders', title=_(u'Row without line')),
    SimpleTerm(value=u'scriptsize', title=_(u'Small font')),
    SimpleTerm(value=u'fullColspan', title=_(u'Strech first line')),
))


ALIGNMENT_VOCABULARY = SimpleVocabulary((
    SimpleTerm(value=u'', title=_(u'automatically')),
    SimpleTerm(value=u'left', title=_(u'left')),
    SimpleTerm(value=u'right', title=_(u'right')),
    SimpleTerm(value=u'center', title=_(u'center')),
))


INDENT_VOCABULARY = SimpleVocabulary((
    SimpleTerm(value=u'', title=_(u'no indent')),
    SimpleTerm(value=u'indent2', title=_(u'2mm')),
    SimpleTerm(value=u'indent10', title=_(u'10mm')),
))


ROWS_VOCABULARY = SimpleVocabulary([
    SimpleTerm(value=u'{}'.format(num),
               title=_('${num} rows', mapping={'num': str(num)}))
    for num in range(6)])


BORDER_LAYOUT_VOCABULARY = SimpleVocabulary((
    SimpleTerm(value='grid',
               title=_(u'table_label_gridLayout',
                       default=u'Grid Layout')),
    SimpleTerm(value='invisible',
               title=_(u'table_label_invisible',
                       default=u'No borders')),
    SimpleTerm(value='fancy_listing',
               title=_(u'table_label_fancy_listing',
                       default=u'Horizontal borders')),
))


class ITableDataRow(Interface):

    column_0 = TextLine(title=_(u'Column ${num}', mapping={'num': 1}),
                        required=False)
    column_1 = TextLine(title=_(u'Column ${num}', mapping={'num': 2}),
                        required=False)
    column_2 = TextLine(title=_(u'Column ${num}', mapping={'num': 3}),
                        required=False)
    column_3 = TextLine(title=_(u'Column ${num}', mapping={'num': 4}),
                        required=False)
    column_4 = TextLine(title=_(u'Column ${num}', mapping={'num': 5}),
                        required=False)
    column_5 = TextLine(title=_(u'Column ${num}', mapping={'num': 6}),
                        required=False)
    column_6 = TextLine(title=_(u'Column ${num}', mapping={'num': 7}),
                        required=False)
    column_7 = TextLine(title=_(u'Column ${num}', mapping={'num': 8}),
                        required=False)
    column_8 = TextLine(title=_(u'Column ${num}', mapping={'num': 9}),
                        required=False)
    column_9 = TextLine(title=_(u'Column ${num}', mapping={'num': 10}),
                        required=False)
    column_10 = TextLine(title=_(u'Column ${num}', mapping={'num': 11}),
                         required=False)
    column_11 = TextLine(title=_(u'Column ${num}', mapping={'num': 12}),
                         required=False)
    row_format = Choice(title=_(u'Format'), vocabulary=ROW_FORMAT_VOCABULARY,
                        required=True,
                        default=u'')


@provider(IFormFieldProvider)
class ITableColumnProperties(Schema):

    mode(columnId='hidden')
    columnId = TextLine(
        title=u'Column ID',
        required=False,
        default=u'',
    )

    active = Bool(
        title=_(u'table_label_active', default=u'Active'),
        required=False,
        default=False)

    alignment = Choice(
        title=_(u'table_label_alignment',
                default=u'Alignment'),
        vocabulary=ALIGNMENT_VOCABULARY,
        required=False,
        default=u'')

    bold = Bool(
        title=_(u'table_label_bold', default=u'Bold'),
        required=False,
        default=False)

    indent = Choice(
        title=_(u'table_label_indent', default=u'Indent'),
        required=False,
        vocabulary=INDENT_VOCABULARY,
        default=u'')

    width = Int(
        title=_(u'table_label_width', default=u'Width (%)'),
        required=False,
        default=10)


def default_column_properties():
    template = {name: ITableColumnProperties[name].default
                for name in ITableColumnProperties.names()}
    values = [template.copy() for num in range(MAX_AMOUNT_OF_COLUMNS)]

    for item in values[:DEFAULT_ACTIVE_COLUMNS]:
        item['active'] = True

    for num in range(len(values)):
        values[num]['columnId'] = u'column_{}'.format(num)

    return values


@provider(IFormFieldProvider)
class ITableSchema(Schema):

    title = TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

    widget(data=DataGridFieldFactory)
    data = List(
        title=_(u'label_table_content', default=u'Table content'),
        required=False,
        value_type=DictRow(schema=ITableDataRow))

    searchable('footnote_text')
    footnote_text = RichText(
        title=_(u'label_footnote_text', default=u'Footnote Text'),
        required=False,
        allowed_mime_types=('text/html',))

    fieldset(
        'layout',
        label=_(u'Layout'),
        fields=(
            'column_properties',
            'header_rows',
            'footer_rows',
            'first_column_is_header',
            'footer_is_bold',
            'border_layout',
            'no_lifting',
        ))

    widget(
        'column_properties', DataGridFieldFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False,
    )
    column_properties = List(
        title=_(u'label_column_properties', default=u'Column properties'),
        required=False,
        value_type=DictRow(schema=ITableColumnProperties),
        defaultFactory=default_column_properties)

    header_rows = Choice(
        title=_(u'label_header_rows', default=u'Amount of header rows'),
        vocabulary=ROWS_VOCABULARY,
        required=True,
        default=u'1')

    footer_rows = Choice(
        title=_(u'label_footer_rows', default=u'Amount of footer rows'),
        vocabulary=ROWS_VOCABULARY,
        required=True,
        default=u'0')

    first_column_is_header = Bool(
        title=_(u'label_first_column_is_header',
                default=u'First column is a header column'),
        default=False)

    footer_is_bold = Bool(
        title=_(u'label_footer_is_bold', default=u'Footer rows are bold'),
        default=True)

    border_layout = Choice(
        title=_(u'label_border_layout', default=u'Border Layout'),
        vocabulary=BORDER_LAYOUT_VOCABULARY,
        default=u'fancy_listing',
        required=True)

    no_lifting = Bool(
        title=_(u'label_no_lifting', default=u'No lifting'),
        description=_(
            u'description_no_lifting',
            default=u'When exporting the book as PDF the table '
            u'will be pulled up if there is no content in the '
            u'first cell. The aim is to place a preceding title '
            u'at the same height as the first row of the table. '
            u'For suppressing this behaviour enable this '
            u'option.'),
        default=False)


class Table(Item):
    implements(ITable)

    def getTable(self):
        return TableGenerator(self).render()

    def getShowTitle(self):
        return self.show_title

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def getColumnProperties(self):
        return self.column_properties

    def getHeaderRows(self, as_int=False):
        if as_int:
            return int(self.header_rows)
        return self.header_rows

    def getFooterRows(self, as_int=False):
        if as_int:
            return int(self.footer_rows)
        return self.footer_rows

    def getFirstColumnIsHeader(self):
        return self.first_column_is_header

    def getFooterIsBold(self):
        return self.footer_is_bold

    def getBorderLayout(self):
        return self.border_layout

    def getNoLifting(self):
        return self.no_lifting


@adapter(Interface, Interface)
class TableBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([
            ('tableExportImport', {
                'class': 'book-sl-toolbar-icon-table-import-export redirect',
                'title': translate(_(u'label_table_export_import',
                                     default=u'Table export / import'),
                                   context=self.request),
                'href': '/table_export_import'
            }),
        ])
