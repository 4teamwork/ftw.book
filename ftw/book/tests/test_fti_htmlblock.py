from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from unittest2 import TestCase



class TestHTMLBlock(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book'))
        self.chapter = create(Builder('chapter').within(self.book))

    @browsing
    def test_creating_htmlblock(self, browser):
        browser.login().visit(self.chapter)
        factoriesmenu.add('HTML Block')

        browser.fill({
                'Title': 'The HTML Block',
                'Show Title': True,
                'HTML': '<p>Some <b>body</b> text</p>'}).submit()
        self.assertEquals(self.chapter.absolute_url() + '/#the-html-block',
                          browser.url)

        blocks = browser.css('.BlockOverallWrapper.html-block')
        self.assertEquals(1, len(blocks),
                          'Expected chapter to have exactly one block')

        block, = blocks
        self.assertEquals(['1.1 The HTML Block'], block.css('h3').text,
                          'Expected block title to be visible.')

        self.assertEquals(
            '<p>Some <b>body</b> text</p>',
            block.css('.sl-text-wrapper').first.normalized_innerHTML)

    @browsing
    def test_showing_block_title(self, browser):
        create(Builder('htmlblock')
               .titled('Visible')
               .having(showTitle=True)
               .within(self.chapter))

        create(Builder('htmlblock')
               .titled('Hidden')
               .having(showTitle=False)
               .within(self.chapter))

        browser.login().visit(self.chapter)
        visible, hidden = browser.css('.BlockOverallWrapper.html-block')

        self.assertEquals(
            ['1.1 Visible'], visible.css('h3').text,
            'Expected block title of the "Visible" block to be visible.')

        self.assertEquals(
            [], hidden.css('h3').text,
            'Expected block title of the "Hidden" block to be hidden.')

    @browsing
    def test_hiding_title_from_table_of_contents(self, browser):
        create(Builder('htmlblock')
               .titled('Block in TOC')
               .having(showTitle=True,
                       hideFromTOC=False)
               .within(self.chapter))

        create(Builder('htmlblock')
                     .titled('Block NOT in TOC')
                     .having(showTitle=True,
                             hideFromTOC=True)
                     .within(self.chapter))

        browser.login().visit(self.chapter)

        self.assertEquals(
            ['1.1 Block in TOC', 'Block NOT in TOC'],
            browser.css('.BlockOverallWrapper.html-block h3').text,
            'Only the first block title should have a number prefix.')

    @browsing
    def test_latex_fields_available(self, browser):
        browser.login().open(self.chapter)
        factoriesmenu.add('HTML Block')

        form = browser.find('Title').parent('form')
        labels = form.field_labels

        self.assertIn('LaTeX code above content', labels)
        self.assertIn('LaTeX code beneath content', labels)

    @browsing
    def test_text_field_is_textarea_for_html(self, browser):
        browser.login().visit(self.chapter)
        factoriesmenu.add('HTML Block')
        self.assertEquals('textarea', browser.find('HTML').tag)
