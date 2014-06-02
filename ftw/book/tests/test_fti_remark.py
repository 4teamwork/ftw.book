from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from unittest2 import TestCase


class TestRemark(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book').titled('The Book'))
        self.chapter = create(Builder('chapter')
                              .titled('The Chapter')
                              .within(self.book))

    @browsing
    def test_creating_remark(self, browser):
        browser.login().visit(self.chapter)
        factoriesmenu.add('Remark')

        browser.fill({
                'Title': 'The Remark',
                'Text': '<p>Some <b>body</b> text</p>'}).submit()
        self.assertEquals(self.chapter.absolute_url() + '/#the-remark',
                          browser.url)

        blocks = browser.css('.BlockOverallWrapper.remark')
        self.assertEquals(1, len(blocks),
                          'Expected chapter to have exactly one block')

        block, = blocks
        self.assertEquals(['The Remark'], block.css('h3').text,
                          'Expected block title to be visible.')

        self.assertEquals(
            '<p>Some <b>body</b> text</p>',
            block.css('.sl-text-wrapper').first.normalized_innerHTML)

    @browsing
    def test_latex_fields_available(self, browser):
        browser.login().open(self.chapter)
        factoriesmenu.add('Remark')

        form = browser.find('Title').parent('form')
        labels = form.field_labels

        self.assertIn('LaTeX code above content', labels)
        self.assertIn('LaTeX code beneath content', labels)

    @browsing
    def test_default_fields_not_visible(self, browser):
        browser.login().open(self.chapter)
        factoriesmenu.add('Remark')

        self.assertFalse(
            browser.find('Description'),
            '"Description" field should not be visible.')

        self.assertFalse(
            browser.find('Show Title'),
            '"Show Title" field should not be visible.')

        self.assertFalse(
            browser.find('Exclude from navigation'),
            '"Exclude from navigation" field should not be visible.')

        self.assertFalse(
            browser.find('Hide from table of contents'),
            '"Hide from table of contents" field should not be visible.')

    @browsing
    def test_remark_does_not_appear_in_navigation(self, browser):
        create(Builder('remark').titled('The Remark').within(self.chapter))

        browser.login().open(self.chapter)
        self.assertItemsEqual(
            ['The Book', 'The Chapter'],
            browser.css('.portletNavigationTree dd a').text)
