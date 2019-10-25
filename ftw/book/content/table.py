from Products import DataGridField
from Products.Archetypes import atapi
from Products.Archetypes.public import DisplayList
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin


MAX_AMOUNT_OF_COLUMNS = 12
MAX_AMOUNT_OF_HEADER_ROWS = 5
MAX_AMOUNT_OF_FOOTER_ROWS = 5
BORDER_LAYOUTS = (
    ('grid', 'Grid Layout'),
    ('invisible', 'No borders'),
    ('fancy_listing', 'Horizontal borders'),
)


table_schema = (ATContentTypeSchema.copy() +
                atapi.Schema((

            atapi.BooleanField(
                name='showTitle',
                schemata='default',
                default=False,
                widget=atapi.BooleanWidget()),

            DataGridField.DataGridField(
                name='data',
                schemata='default',
                searchable=True,
                required=False,
                columns=['column_%i' % i for i in
                         range(MAX_AMOUNT_OF_COLUMNS)] + ['row_format'],
                widget=DataGridField.DataGridWidget(
                    macro='datagridwidget_bibliothek_table',
                    columns=dict([
                        ('column_%i' % i, DataGridField.Column(
                            label='Column ' + i))
                        for i in range(MAX_AMOUNT_OF_COLUMNS)] + [(
                            'row_format',
                            DataGridField.SelectColumn(
                                label='Format',
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
                allowable_content_types=('text/html', ),
                default_content_type='text/html',
                validators=('isTidyHtmlWithCleanup', ),
                default_input_type='text/html',
                default_output_type='text/x-html-safe',
                widget=atapi.RichWidget()),

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
                    columns={
                        'columnId': DataGridField.FixedColumn(
                            'column_id',
                            default='column_x',
                            visible=False,
                            ),
                        'columnTitle': DataGridField.FixedColumn(
                            'Column',
                            default='Row X',
                            ),
                        'active': DataGridField.CheckboxColumn(
                            'Active',
                            default=False,
                            ),
                        'alignment': DataGridField.SelectColumn(
                            'Alignment',
                            vocabulary='getAlignmentVocabulary',
                            ),
                        'bold': DataGridField.CheckboxColumn(
                            'Bold',
                            default=False,
                            ),
                        'indent': DataGridField.SelectColumn(
                            'Indent',
                            vocabulary='getIndentVocabulary',
                            ),
                        'width': DataGridField.Column(
                            'Width (%)',
                            ),
                        },
                    ),
                fixed_rows=[
                    DataGridField.FixedRow(
                        keyColumn='columnId',
                        initialData={
                            'columnId': 'column_%i' % (i),
                            'columnTitle': u'Column ' + i,
                            'active': False,
                            'alignment': '',
                            'bold': False,
                            'indent': '',
                            'width': '10',
                            },
                        ) for i in range(MAX_AMOUNT_OF_COLUMNS)],
                ),

            atapi.StringField(
                name='headerRows',
                schemata='Layout',
                default='1',
                enforceVocabulary=True,
                vocabulary=[
                    (str(i), str(i) + ' rows')
                    for i in range(MAX_AMOUNT_OF_HEADER_ROWS + 1)],
                widget=atapi.SelectionWidget()),

            atapi.StringField(
                name='footerRows',
                schemata='Layout',
                default=0,
                enforceVocabulary=True,
                vocabulary=[
                    (str(i), str(i) + ' rows')
                    for i in range(MAX_AMOUNT_OF_FOOTER_ROWS + 1)],
                widget=atapi.SelectionWidget()),

            atapi.BooleanField(
                name='firstColumnIsHeader',
                schemata='Layout',
                default=False,
                widget=atapi.BooleanWidget()),

            atapi.BooleanField(
                name='footerIsBold',
                schemata='Layout',
                default=True,
                widget=atapi.BooleanWidget()),

            atapi.StringField(
                name='borderLayout',
                schemata='Layout',
                default='fancy_listing',
                enforceVocabulary=True,
                vocabulary=BORDER_LAYOUTS,
                widget=atapi.SelectionWidget()),

            atapi.BooleanField(
                name='noLifting',
                schemata='Layout',
                default=False,
                widget=atapi.BooleanWidget()),

            )))


class Table(ATCTContent, HistoryAwareMixin):
    portal_type = "Table"
    schema = table_schema

    def getAlignmentVocabulary(self):
        return DisplayList((
                ('', 'automatically'),
                ('left', 'left'),
                ('right', 'right'),
                ('center', 'center'),
                ))

    def getIndentVocabulary(self):
        return DisplayList((
                ('', 'no indent'),
                ('indent2', '2mm'),
                ('indent10', '10mm'),
                ))

    def getRowFormatVocabulary(self):
        return DisplayList((
                ('', 'Normal'),
                ('bold', 'Bold'),
                ('grey', 'Grey font'),

                ('indent2', '2mm indent'),
                ('indent10', '10mm indent'),
                ('indent2 bold', '2mm ind. + bold'),
                ('indent10 bold', '10mm ind. + bold'),
                ('indent2 grey', '2mm ind. + grey font'),
                ('indent10 grey', '10mm ind. + grey font'),

                ('noborders', 'Row without line'),
                ('scriptsize', 'Small font'),
                ('fullColspan', 'Strech first line'),
                ))


atapi.registerType(Table, 'ftw.book')
