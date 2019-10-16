from ftw.book.table.generator import TableGenerator
from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
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
