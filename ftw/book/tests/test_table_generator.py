# coding=utf-8
from ftw.book.table.generator import TableGenerator
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.testing import MockTestCase


class Table(object):
    """ Dummy table class representing the table-content-type
    to test the TableGenerator class
    """
    def __init__(self, *args, **kwargs):
        self.data = kwargs.get('data', '')
        self.columnProperties = kwargs.get('column_properties', '')
        self.borderLayout = kwargs.get('border_layout', '')
        self.noLifting = kwargs.get('no_lifting', False)
        self.showTitle = kwargs.get('show_title', False)
        self.headerRows = kwargs.get('header_rows', 0)
        self.footerRows = kwargs.get('footer_rows', 0)
        self.firstColumnIsHeader = kwargs.get(
            'first_column_is_header', False)
        self.footerIsBold = kwargs.get('footer_is_bold', False)
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')

    def Title(self):
        return self.title

    def Description(self):
        return self.description

    def getData(self):
        return self.data

    def getColumnProperties(self):
        return self.columnProperties

    def getBorderLayout(self):
        return self.borderLayout

    def getNoLifting(self):
        return self.noLifting

    def getShowTitle(self):
        return self.showTitle

    def getHeaderRows(self, *args, **kwargs):
        return self.headerRows

    def getFooterRows(self, *args, **kwargs):
        return self.footerRows

    def getFirstColumnIsHeader(self):
        return self.firstColumnIsHeader

    def getFooterIsBold(self):
        return self.footerIsBold


class TestTableGenerator(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestTableGenerator, self).setUp()

        self.column_properties = ({
          'active': '1',
          'alignment': 'left',
          'bold': '',
          'columnId': 'column_0',
          'columnTitle': 'Spalte 1',
          'indent': '',
          'width': '10'},
         {'active': '1',
          'alignment': 'right',
          'bold': '',
          'columnId': 'column_1',
          'columnTitle': 'Spalte 2',
          'indent': '',
          'width': '40'},
         {'active': '1',
          'alignment': 'center',
          'bold': '',
          'columnId': 'column_2',
          'columnTitle': 'Spalte 3',
          'indent': 'indent2',
          'width': '10'},
         {'active': '1',
          'alignment': '',
          'bold': '',
          'columnId': 'column_3',
          'columnTitle': 'Spalte 4',
          'indent': '',
          'width': '30'},
         {'active': '1',
          'alignment': '',
          'bold': '',
          'columnId': 'column_4',
          'columnTitle': 'Spalte 5',
          'indent': '',
          'width': '10'},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_5',
          'columnTitle': 'Spalte 6',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_6',
          'columnTitle': 'Spalte 7',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_7',
          'columnTitle': 'Spalte 8',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_8',
          'columnTitle': 'Spalte 9',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_9',
          'columnTitle': 'Spalte 10',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_10',
          'columnTitle': 'Spalte 11',
          'indent': '',
          'width': ''},
         {'active': '',
          'alignment': '',
          'bold': '',
          'columnId': 'column_11',
          'columnTitle': 'Spalte 12',
          'indent': '',
          'width': ''})

        self.datagrid_data = ({
          'column_0': u'Vörname',
          'column_1': u'Näme',
          'column_2': u'Wühnort',
          'column_3': u'Homepage',
          'column_4': '',
          'column_5': '',
          'column_6': '',
          'column_7': '',
          'column_8': '',
          'column_9': '',
          'column_10': '',
          'column_11': '',
          'row_format': ''},
         {'column_0': 'James',
          'column_1': 'Bond',
          'column_2': 'Secret &Service: !',
          'column_3': 'Visit <a href="http://007.com/">my cool website</a> now!',
          'column_4': '',
          'column_5': '',
          'column_6': '',
          'column_7': '',
          'column_8': '',
          'column_9': '',
          'column_10': '',
          'column_11': '',
          'row_format': 'indent2'},
         {'column_0': 'Bud',
          'column_1': 'Spencer',
          'column_2': 'Italien <sup>1</sup> <br> Europe',
          'column_3': 'Visit <a href="http://en.budspencerofficial.com/">my cool website</a> now!',
          'column_4': '',
          'column_5': '',
          'column_6': '',
          'column_7': '',
          'column_8': '',
          'column_9': '',
          'column_10': '',
          'column_11': '',
          'row_format': 'indent10 bold'},)

    def test_full_generator(self):
        """ Create a full table and test the output superficial without
        testing every function itself.
        """
        table = Table(
            data=self.datagrid_data,
            column_properties=self.column_properties,
            border_layout='grid',
            show_title=True,
            header_rows=1,
            footer_rows=1,
            title="My Test Täble",
            description="Its ä Description",
            )

        generator = TableGenerator(table)
        html_table = generator.render()

        title = [
            '<caption>',
                'My Test Täble',
            '</caption>',
        ]
        colgroup = [
            '<colgroup> ',
                '<col width="10%"/>',
                '<col width="40%"/>',
                '<col width="10%"/>',
                '<col width="30%"/>',
                '<col width="10%"/>',
            '</colgroup>',
        ]
        thead = [
            '<thead> '
                '<tr> '
                    '<th align="left" ',
                    'class=" border-right border-bottom border-top border-left left" ',
                    'id="column_0">Vörname</th>',
                    '<th align="left" ',
                    'class=" right border-right border-bottom border-top border-left" ',
                    'id="column_1">Näme</th>',
                    '<th align="left" ',
                    'class=" center border-right border-bottom border-top indent2 border-left" ',
                    'id="column_2">Wühnort</th>',
                    '<th align="left" ',
                    'class=" border-right border-top border-left border-bottom" ',
                    'id="column_3">Homepage</th>',
                    '<th align="left" ',
                    'class=" border-right border-top border-left border-bottom" ',
                    'id="column_4"> </th>',
                '</tr>'
            '</thead>',
        ]
        tbody = [
            '<tbody> ',
                '<tr> ',
                    '<td class="border-left border-bottom border-top indent2 border-right left" ',
                    'headers="column_0">James</td>',
                    '<td class="border-right border-left border-top right border-bottom" ',
                    'headers="column_1">Bond</td>',
                    '<td class="center border-left border-bottom border-top indent2 border-right" ',
                    'headers="column_2">Secret &amp;Service: !</td>',
                    '<td class="border-right border-top border-left border-bottom" ',
                    'headers="column_3">Visit <a href="http://007.com/">my cool website</a> now!</td>',
                    '<td class="border-right border-top border-left border-bottom" ',
                    'headers="column_4"> </td>',
                '</tr>',
            '</tbody>',
        ]
        tfoot = [
            '<tfoot> ',
                '<tr> ',
                    '<td class="bold border-right border-bottom border-top border-left indent10 left">',
                    'Bud</td>',
                    '<td class="right bold border-left border-bottom border-top border-right">',
                    'Spencer</td>',
                    '<td class="center border-right border-bottom border-top indent2 border-left bold">',
                    'Italien <sup>1</sup> <br/> Europe</td>',
                    '<td class="border-right border-top border-left bold border-bottom">Visit <a href="http://en.budspencerofficial.com/">my cool website</a> now!</td>',
                    '<td class="border-right border-top border-left bold border-bottom"> </td>',
                '</tr>',
            '</tfoot>',
        ]

        self.assertIn(''.join(title), html_table)
        self.assertIn(''.join(colgroup), html_table)
        self.assertIn(''.join(thead), html_table)
        self.assertIn(''.join(tbody), html_table)
        self.assertIn(''.join(tfoot), html_table)
