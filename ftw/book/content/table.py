from Products import DataGridField
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.Archetypes import atapi
from Products.Archetypes.public import DisplayList
from ftw.book import _
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import ITable
from ftw.book.table import generator
from zope.interface import implements
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.types.common.content import simplelayout_schemas


MAX_AMOUNT_OF_COLUMNS = 12
MAX_AMOUNT_OF_HEADER_ROWS = 5
MAX_AMOUNT_OF_FOOTER_ROWS = 5
BORDER_LAYOUTS = (
    ('grid', _(u'izug_label_gridLayout', default=u'Grid Layout')),
    ('lines', _(u'izug_label_linesLayout', default=u'Underline every row')),
    ('vertical', _(u'izug_label_verticalLayout', default=u'Vertical grid')),
    )


table_schema = (ATContentTypeSchema.copy() + \
                   atapi.Schema((

            atapi.BooleanField(
                name='showTitle',
                schemata='default',
                default=False,
                widget=atapi.BooleanWidget(
                    label='Show title',
                    label_msgid='izug_label_showtitle',
                    description='',
                    description_msgid='izug_help_showtitle',
                    i18n_domain='izug',
                    ),
                ),

            DataGridField.DataGridField(
                name='data',
                schemata='default',
                searchable=False,
                required=False,
                columns=['column_%i' % i for i in
                         range(MAX_AMOUNT_OF_COLUMNS)] + ['row_format'],
                widget=DataGridField.DataGridWidget(
                    label='Tabellen Inhalt',
                    macro='datagridwidget_bibliothek_table',
                    columns=dict(
                        [
                            ('column_%i' % i, DataGridField.Column(
                                    label='Spalte %i' % (i + 1)))
                            for i in range(MAX_AMOUNT_OF_COLUMNS)] + [(
                                'row_format',
                                DataGridField.SelectColumn(
                                    title='Format',
                                    vocabulary='getRowFormatVocabulary',
                                    ),
                                )]
                        ),
                    ),
                ),

            atapi.TextField(
                name='footnoteText',
                schemata='default',
                required=False,
                searchable=True,
                default_input_type='text/html',
                default_output_type='text/html',
                widget=atapi.RichWidget(
                    label='Footnote Text',
                    label_msgid='izug_label_footnoteText',
                    description='',
                    description_msgid='izug_help_footnoteText',
                    i18n_domain='izug.bibliothek',
                    ),
                ),

            DataGridField.DataGridField(
                name='columnProperties',
                schemata='Layout',
                searchable=False,
                required=False,
                allow_insert=False,
                allow_delete=False,
                allow_reorder=False,
                columns=(
                    'columnId',
                    'columnTitle',
                    'active',
                    'alignment',
                    'bold',
                    'indent',
                    'width',
                    ),
                widget=DataGridField.DataGridWidget(
                    label='Column Properties',
                    label_msgid='izug_label_columnProperties',
                    i18n_domain='izug',
                    columns={
                        'columnId': DataGridField.FixedColumn(
                            'column_id',
                            default='column_x',
                            visible=False,
                            ),
                        'columnTitle': DataGridField.FixedColumn(
                            _(u'izug_label_column', default=u'Column'),
                            default='Spalte X',
                            ),
                        'active': DataGridField.CheckboxColumn(
                            _(u'izug_label_active', default=u'Active'),
                            default=False,
                            ),
                        'alignment': DataGridField.SelectColumn(
                            _(u'izug_label_alignment', default=u'Alignment'),
                            vocabulary='getAlignmentVocabulary',
                            ),
                        'bold': DataGridField.CheckboxColumn(
                            _(u'izug_label_bold', default=u'Bold'),
                            default=False,
                            ),
                        'indent': DataGridField.SelectColumn(
                            _(u'izug_label_indent', default=u'Indent'),
                            vocabulary='getIndentVocabulary',
                            ),
                        'width': DataGridField.Column(
                            label=_(u'izug_label_width',
                                      default=u'Width (%)'),
                            ),
                        },
                    ),
                fixed_rows=[
                    DataGridField.FixedRow(
                        keyColumn='columnTitle',
                        initialData={
                            'columnId':'column_%i' % (i),
                            'columnTitle': 'Spalte %i' % (i + 1),
                            'active': False,
                            'alignment': '',
                            'bold': False,
                            'indent': '',
                            },
                        ) for i in range(MAX_AMOUNT_OF_COLUMNS)],
                ),

            atapi.StringField(
                name='headerRows',
                schemata='Layout',
                default='1',
                enforceVocabulary=True,
                vocabulary=[
                    (str(i), '%i Zeilen' % i) for i
                    in range(MAX_AMOUNT_OF_HEADER_ROWS + 1)],
                widget=atapi.SelectionWidget(
                    label='Amount of header rows',
                    label_msgid='izug_label_headerRows',
                    description='',
                    description_msgid='izug_help_headerRows',
                    i18n_domain='izug'
                    ),
                ),

            atapi.StringField(
                name='footerRows',
                schemata='Layout',
                default=0,
                enforceVocabulary=True,
                vocabulary=[
                    (str(i), '%i Zeilen' % i) for i
                    in range(MAX_AMOUNT_OF_FOOTER_ROWS+1)],
                widget=atapi.SelectionWidget(
                    label='Amount of footer rows',
                    label_msgid='izug_label_footerRows',
                    description='',
                    description_msgid='izug_help_footerRows',
                    i18n_domain='izug'
                    ),
                ),

            atapi.BooleanField(
                name='firstColumnIsHeader',
                schemata='Layout',
                default=False,
                widget=atapi.BooleanWidget(
                    label='First column is a header column',
                    label_msgid='izug_label_firstColumnIsHeader',
                    description='Select this Option if the first column ' + \
                        'contain row headers',
                    description_msgid='izug_help_firstColumnIsHeader',
                    i18n_domain='izug',
                    ),
                ),

            atapi.BooleanField(
                name='headerIsBold',
                schemata='Layout',
                default=True,
                widget=atapi.BooleanWidget(
                    label='Header rows are bold',
                    label_msgid='izug_label_headerIsBold',
                    description='',
                    description_msgid='izug_help_headerIsBold',
                    i18n_domain='izug.bibliothek',
                    ),
                ),

            atapi.BooleanField(
                name='footerIsBold',
                schemata='Layout',
                default=True,
                widget=atapi.BooleanWidget(
                    label='Footer rows are bold',
                    label_msgid='izug_label_footerIsBold',
                    description='',
                    description_msgid='izug_help_footerIsBold',
                    i18n_domain='izug.bibliothek',
                    ),
                ),

            atapi.StringField(
                name='borderLayout',
                schemata='Layout',
                default='lines',
                enforceVocabulary=True,
                vocabulary=BORDER_LAYOUTS,
                widget=atapi.SelectionWidget(
                    label='Border Layout',
                    label_msgid='izug_label_borderLayout',
                    description='',
                    description_msgid='izug_help_borderLayout',
                    i18n_domain='izug',
                    )
                ),

            atapi.BooleanField(
                name='noLifting',
                schemata='Layout',
                default=False,
                widget=atapi.BooleanWidget(
                    label='No lifting',
                    label_msgid='izug_label_no-lifting',
                    description='',
                    description_msgid='izug_help_no-lifting',
                    i18n_domain='izug.bibliothek',
                    )),

            )))

# We need a text-field if we inherit from ATDocumentBase
table_schema += simplelayout_schemas.textSchema.copy()
table_schema['text'].widget.visible = {'edit': 0, 'view': 0}

simplelayout_schemas.finalize_simplelayout_schema(table_schema)


class Table(ATDocumentBase):
    """A Table for iZug Bibliothek"""
    implements(ITable, ISimpleLayoutBlock)

    portal_type = "Table"
    schema = table_schema

    def getTable(self):
        return generator.TableGenerator(self).render()

    def convert_to_int(self, value):
        """ Converts a value to integer. If its not possible we return the
        unconverted value
        """
        try:
            return int(value)
        except ValueError:
            return value

    def getHeaderRows(self, as_int=False):
        """ We need to calculate with the keys of the headerRows. So we need
        integers. But the vocabulary of a ATField needs strings as keys.
        """
        if as_int:
            return self.convert_to_int(self.headerRows)
        return self.headerRows

    def getFooterRows(self, as_int=False):
        """ We need to calculate with the keys of the footerRsows. So we need
        integers. But the vocabulary of a ATField needs strings as keys.
        """
        if as_int:
            return self.convert_to_int(self.footerRows)
        return self.footerRows

    def getAlignmentVocabulary(self):
        return DisplayList((
                ('', _('automatically')),
                ('left', _('left')),
                ('right', _('right')),
                ('center', _('center')),
                ))

    def getIndentVocabulary(self):
        return DisplayList((
                ('', _('no indent')),
                ('indent2', _('2mm')),
                ('indent10', _('10mm')),
                ))

    def getRowFormatVocabulary(self):
        return DisplayList((
                ('', 'Normal'),
                ('bold', 'Fett'),
                ('indent2', '2mm Einruecken'),
                ('indent10', '10mm Einruecken'),
                ('indent2 bold', '2mm Einr. + Fett'),
                ('indent10 bold', '10mm Einr. + Fett'),
                ('noborders', 'Leerzeile ohne Linie'),
                ('grey', 'Graue schrift'),
                ('scriptsize', 'Kleine Schrift'),
                ('fullColspan', 'Erste Zelle strecken'),
                ))

atapi.registerType(Table, PROJECTNAME)
