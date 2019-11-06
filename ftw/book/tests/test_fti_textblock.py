from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from operator import attrgetter
from plone.app.textfield.value import RichTextValue
from textwrap import dedent
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

        self.assertEquals(
            u'<h2 class="toc3">The Text Block</h2>',
            browser.css('.sl-block h2').first.outerHTML)

    @browsing
    def test_showing_block_title(self, browser):
        self.grant('Manager')

        title = 'First things first'
        self.textblock.show_title = False
        transaction.commit()
        browser.login().visit(self.textblock)
        self.assertNotIn(title, browser.css('.sl-block h2').text)

        self.textblock.show_title = True
        transaction.commit()
        browser.reload()
        self.assertIn(title, browser.css('.sl-block h2').text)

    @browsing
    def test_hiding_title_from_table_of_contents_removes_prefix(self, browser):
        self.grant('Manager')
        self.textblock.show_title = True

        self.textblock.hide_from_toc = False
        transaction.commit()
        browser.login().visit(self.textblock)
        self.assertIn(
            u'<h2 class="toc4">First things first</h2>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h2')))

        self.textblock.hide_from_toc = True
        transaction.commit()
        browser.reload()
        self.assertIn(
            u'<h2 class="no-toc">First things first</h2>',
            map(attrgetter('outerHTML'), browser.css('.sl-block h2')))

    @browsing
    def test_warning_when_table_widths_not_specified(self, browser):
        browser.login().open(self.textblock)
        statusmessages.assert_no_messages()

        self.textblock.text = RichTextValue(dedent(r'''
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
        statusmessages.assert_message(
            'Please specify the width of the table columns / cells')
