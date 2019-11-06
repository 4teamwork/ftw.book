from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from operator import attrgetter
from plone.app.textfield.value import RichTextValue
from textwrap import dedent
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
            u'<h2 class="toc3">The HTML Block</h2>',
            browser.css('.sl-block h2').first.outerHTML)

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
        self.assertNotIn(title, browser.css('.sl-block h2').text)

        self.htmlblock.show_title = True
        transaction.commit()
        browser.reload()
        self.assertIn(title, browser.css('.sl-block h2').text)

    @browsing
    def test_no_prefix_when_hiding_title_from_table_of_contents(self, browser):
        self.grant('Manager')
        self.htmlblock.show_title = True

        self.htmlblock.hide_from_toc = False
        transaction.commit()
        browser.login().visit(self.htmlblock)
        self.assertIn(
            u'<h2 class="toc3">An HTML Block</h2>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h2')))

        self.htmlblock.hide_from_toc = True
        transaction.commit()
        browser.reload()
        self.assertIn(
            u'<h2 class="no-toc">An HTML Block</h2>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h2')))

    @browsing
    def test_warning_when_table_widths_not_specified(self, browser):
        browser.login().open(self.htmlblock)
        statusmessages.assert_no_messages()

        self.htmlblock.content = RichTextValue(dedent(r'''
        <p>ok:</p>
        <table>
          <tr><td width="100%">foo</td></tr>
        </table>
        <p>not ok:</p>
        <table>
          <tr><td>bar</td></tr>
        </table>
        '''), mimeType='text/html', outputMimeType='text/html')
        transaction.commit()
        browser.reload()

        browser.reload()
        statusmessages.assert_message(
            'Please specify the width of the table columns / cells')
