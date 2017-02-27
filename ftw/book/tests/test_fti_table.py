from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
import transaction


class TestTable(FunctionalTestCase):

    @browsing
    def test_creating_table(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book.empty)
        factoriesmenu.add('Table')
        browser.fill({
            'Title': 'The Table',
            'Show title': True}).submit()

        self.assertEquals(self.example_book.empty.absolute_url() + '#the-table',
                          browser.url)
        self.assertEquals(1, len(browser.css('.sl-block')),
                          'Expected chapter to have exactly one block')

        self.assertEquals(
            'The table has no content yet.'
            ' Edit the table block for adding content.',
            browser.css('.ftw-book-table .portalMessage dd').first.text)

    @browsing
    def test_table_is_rendered(self, browser):
        browser.login().visit(self.table)
        self.assertEquals(
            [{'City': 'Guangzhou', 'Population': '44 mil 1', 'Ranking': '1'},
             {'City': 'Shanghai', 'Population': '35 mil', 'Ranking': '2'},
             {'City': 'Chongqing', 'Population': '30 mil', 'Ranking': '3'}],
            browser.css('.ftw-book-table table').first.dicts())

    @browsing
    def test_hiding_block_title(self, browser):
        self.grant('Manager')

        title = 'Population'
        self.table.show_title = False
        transaction.commit()
        browser.login().visit(self.table)
        self.assertNotIn(title, browser.css('.sl-block table caption').text)

        self.table.show_title = True
        transaction.commit()
        browser.reload()
        self.assertIn(title, browser.css('.sl-block table caption').text)
