from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
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
    def test_table_is_rendered_rendering(self, browser):
        create(Builder('table')
               .titled('The Table')
               .having(showTitle=True)
               .with_table([['Foo', 'Bar'],
                            ['1', '2'],
                            ['3', '4']])
               .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)

        self.assertEquals(
            [{'Foo': '1',
              'Bar': '2'},
             {'Foo': '3',
              'Bar': '4'}],
            browser.css('.ftw-book-table table').first.dicts())

    @browsing
    def test_hiding_block_title(self, browser):
        self.grant('Manager')
        table = create(Builder('table')
                       .titled('Visible')
                       .with_dummy_table()
                       .having(show_title=True)
                       .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)
        self.assertEquals(
            ['Visible'],
            browser.css('.sl-block table caption').text)

        table.show_title = False
        transaction.commit()
        browser.reload()
        self.assertEquals(
            [],
            browser.css('.sl-block table caption').text)
