from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
import transaction


class TestTextBlock(FunctionalTestCase):

    @browsing
    def test_creating_textblock(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book.empty)
        factoriesmenu.add('TextBlock')
        browser.fill({
                'Title': 'The Text Block',
                'Show title': True,
                'Text': '<b>Some body text</b>'}).submit()
        self.assertEquals(
            self.example_book.empty.absolute_url() + '#the-text-block',
            browser.url)
        self.assertEquals(1, len(browser.css('.sl-block')),
                          'Expected chapter to have exactly one block')

        self.assertEquals(['3.1 The Text Block'],
                          browser.css('.sl-block h3').text,
                          'Expected block title to be visible.')

    @browsing
    def test_showing_block_title(self, browser):
        self.grant('Manager')
        block = create(Builder('book textblock')
                       .titled('The Textblock')
                       .having(show_title=True)
                       .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)
        self.assertEquals(
            ['3.1 The Textblock'],
            browser.css('.sl-block h3').text)

        block.show_title = False
        transaction.commit()
        browser.reload()
        self.assertEquals(
            [],
            browser.css('.sl-block h3').text)

    @browsing
    def test_hiding_title_from_table_of_contents_removes_prefix(self, browser):
        self.grant('Manager')
        block = create(Builder('book textblock')
                       .titled('The Textblock')
                       .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)
        self.assertEquals(
            ['3.1 The Textblock'],
            browser.css('.sl-block h3').text)

        block.hide_from_toc = True
        transaction.commit()
        browser.reload()
        self.assertEquals(
            ['The Textblock'],
            browser.css('.sl-block h3').text)
