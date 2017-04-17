from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from operator import attrgetter
import transaction


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

        self.assertEquals(
            u'<h3 class="toc3">The HTML Block</h3>',
            browser.css('.sl-block h3').first.outerHTML)

        self.assertEquals(
            'Some <b>body</b> text',
            browser.css('.sl-block p').first.normalized_innerHTML)

    @browsing
    def test_hiding_block_title(self, browser):
        self.grant('Manager')

        title = 'An HTML Block'
        self.htmlblock.show_title = False
        transaction.commit()
        browser.login().visit(self.htmlblock)
        self.assertNotIn(title, browser.css('.sl-block h3').text)

        self.htmlblock.show_title = True
        transaction.commit()
        browser.reload()
        self.assertIn(title, browser.css('.sl-block h3').text)

    @browsing
    def test_no_prefix_when_hiding_title_from_table_of_contents(self, browser):
        self.grant('Manager')
        self.htmlblock.show_title = True

        self.htmlblock.hide_from_toc = False
        transaction.commit()
        browser.login().visit(self.htmlblock)
        self.assertIn(
            u'<h3 class="toc3">An HTML Block</h3>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h3')))

        self.htmlblock.hide_from_toc = True
        transaction.commit()
        browser.reload()
        self.assertIn(
            u'<h3 class="no-toc">An HTML Block</h3>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h3')))
