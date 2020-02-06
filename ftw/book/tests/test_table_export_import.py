from ftw.book.table.generator import TableGenerator
from ftw.book.tests import FunctionalTestCase
from ftw.book.tests.builders import asset
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPServerError
from plone.app.textfield.value import RichTextValue
import textwrap


class TestTableExportImport(FunctionalTestCase):

    def setUp(self):
        super(TestTableExportImport, self).setUp()
        self.table = self.example_book.unrestrictedTraverse(
            'historical-background/china/population')

    @browsing
    def test_export_table(self, browser):
        browser.login().visit(self.table, view='table_export_import')
        browser.click_on('Export')

        self.assertEqual(textwrap.dedent('''
        http://nohost/plone/the-example-book/historical-background/china/population;;
        Ranking;City;Population
        1;Guangzhou;44 mil <sup>1</sup>
        2;Shanghai;35 mil
        3;Chongqing;30 mil
        ''').replace('\n', '\r\n').strip(), browser.contents.strip())

        self.assertEqual(
            'text/csv; charset=utf-8',
            browser.headers.get('content-type'))

    @browsing
    def test_non_ascii_export(self, browser):
        table2 = create(Builder('table')
                        .titled(u'Population')
                        .with_table((('Ranking', 'City', 'Population'),
                                     ('0', u'Gu\xe4ngzhou', '44 mil <sup>1</sup>')))
                        .having(border_layout='grid',
                                footnote_text=RichTextValue(
                                    u'<p><sup>1</sup> thats quite big</p>'))
                        .within(self.table.aq_parent))
        browser.login().visit(table2, view='table_export_import')
        try:
            browser.click_on('Export')
        except HTTPServerError:
            self.fail('Export should work non ascii chars in the table')

    @browsing
    def test_bom_encoded_import(self, browser):
        self.assert_table_display(
            [['Ranking', 'City', 'Population'],
             ['1', 'Guangzhou', '44 mil 1'],
             ['2', 'Shanghai', '35 mil'],
             ['3', 'Chongqing', '30 mil']])

        csvfile = (u'http://nohost/plone/the-example-book/historical-background/china/population;;\n\r'
                   u'Ranking;City;Population\r\n'
                   u'1;Gu\xe4ngzhou;100 mil').encode('utf-8-sig')  # Encode as utf-8 with BOM

        browser.login().visit(self.table, view='table_export_import')
        browser.fill({'Modified CSV-file:': (csvfile, 'file.csv', 'text/csv'),
                      'Columns to import': 'City (Spalte 2)'})

        browser.click_on('Import')

        self.assert_table_display(
            [['Ranking', 'City', 'Population'],
             ['1', u'Gu\xc3\xa4ngzhou', '44 mil 1'],
             ['2', 'Shanghai', '35 mil'],
             ['3', 'Chongqing', '30 mil']])

    @browsing
    def test_import_table(self, browser):
        self.assert_table_display(
            [['Ranking', 'City', 'Population'],
             ['1', 'Guangzhou', '44 mil 1'],
             ['2', 'Shanghai', '35 mil'],
             ['3', 'Chongqing', '30 mil']])

        csvfile = textwrap.dedent('''
        http://nohost/plone/the-example-book/historical-background/china/population;;
        Ranking;City;Population!!!!!!!
        1;Guangzhou;100 mil
        2;Shanghai;101 mil
        3;Chongqing;102 mil
        ''').replace('\n', '\r\n').strip()
        browser.login().visit(self.table, view='table_export_import')
        browser.fill({'Modified CSV-file:': (csvfile, 'file.csv', 'text/csv'),
                      'Columns to import': 'Population (Spalte 3)'})
        browser.click_on('Import')

        self.assert_table_display(
            [['Ranking', 'City', 'Population'],
             ['1', 'Guangzhou', '100 mil'],
             ['2', 'Shanghai', '101 mil'],
             ['3', 'Chongqing', '102 mil']])

    def assert_table_display(self, expected):
        with Browser() as browser:
            browser.open_html(TableGenerator(self.table).render())
            got = browser.css('table').first.lists()

        self.assertEqual(expected, got)
