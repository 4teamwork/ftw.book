from Acquisition import aq_parent
from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
import transaction


class TestListingBlock(FunctionalTestCase):

    @browsing
    def test_create_listingblock(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book.empty)
        factoriesmenu.add('File listing block')
        browser.fill({
            'Title': 'Recipes',
            'Show title': True,
            'Hide from table of contents': False,
            'Columns': ['Title', 'modified']}).submit()

        self.assertEquals(
            self.example_book.empty.absolute_url() + '/recipes/folder_contents',
            browser.url)

        browser.open(self.example_book.empty)
        self.assertEquals(1, len(browser.css('.sl-block')),
                          'Expected chapter to have exactly one block')

        self.assertEquals(['3.1 Recipes'],
                          browser.css('.sl-block h3').text,
                          'Expected block title to be visible.')

    @browsing
    def test_showing_block_title(self, browser):
        title = '2.1.3 Important Documents'
        selector = '.sl-block h4'

        self.grant('Manager')
        browser.login().visit(aq_parent(self.listingblock))
        self.assertIn(title, browser.css(selector).text)

        self.listingblock.show_title = False
        transaction.commit()
        browser.reload()
        self.assertNotIn(title, browser.css(selector).text)

    @browsing
    def test_hiding_title_from_table_of_contents_removes_prefix(self, browser):
        self.grant('Manager')
        browser.login().visit(aq_parent(self.listingblock))
        self.assertIn('2.1.3 Important Documents',
                      browser.css('.sl-block h4').text)

        self.listingblock.hide_from_toc = True
        transaction.commit()
        browser.reload()
        self.assertIn('Important Documents',
                      browser.css('.sl-block h4').text)
