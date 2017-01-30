from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestHTMLBlock(FunctionalTestCase):

    @browsing
    def test_creating_htmlblock(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book.empty)
        factoriesmenu.add('HTML block')

        browser.fill({
            'Title': 'The HTML Block',
            'Show title': True,
            'Content': '<p>Some <b>body</b> text</p>'}).submit()

        self.assertEquals(
            self.example_book.empty.absolute_url() + '#the-html-block',
            browser.url)

        self.assertEquals(1, len(browser.css('.sl-block')),
                          'Expected chapter to have exactly one block')

        self.assertEquals(['3.1 The HTML Block'],
                          browser.css('.sl-block h3').text,
                          'Expected block title to be visible.')

        self.assertEquals(
            'Some <b>body</b> text',
            browser.css('.sl-block p').first.normalized_innerHTML)

    @browsing
    def test_hiding_block_title(self, browser):
        self.grant('Manager')
        create(Builder('book htmlblock')
               .titled('Visible')
               .having(show_title=True)
               .within(self.example_book.empty))

        create(Builder('book htmlblock')
               .titled('Hidden')
               .having(show_title=False)
               .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)
        self.assertEquals(
            ['3.1 Visible'],
            browser.css('.sl-block h3').text)

    @browsing
    def test_no_prefix_when_hiding_title_from_table_of_contents(self, browser):
        self.grant('Manager')
        create(Builder('book htmlblock')
               .titled('Block in TOC')
               .having(show_title=True, hide_from_toc=False)
               .within(self.example_book.empty))

        create(Builder('book htmlblock')
               .titled('Block NOT in TOC')
               .having(show_title=True, hide_from_toc=True)
               .within(self.example_book.empty))

        browser.login().visit(self.example_book.empty)
        self.assertEquals(
            ['3.1 Block in TOC', 'Block NOT in TOC'],
            sorted(browser.css('.sl-block h3').text))
