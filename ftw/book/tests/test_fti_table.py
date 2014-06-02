from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from unittest2 import TestCase


class TestTable(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book'))
        self.chapter = create(Builder('chapter').within(self.book))

    @browsing
    def test_creating_table(self, browser):
        browser.login().visit(self.chapter)
        factoriesmenu.add('Table')
        browser.fill({
                'Title': 'The Table',
                'Show title': True,
                'columnProperties.active.1': True,
                'columnProperties.active.2': True}).submit()

        self.assertEquals(self.chapter.absolute_url() + '/#the-table',
                          browser.url)
        blocks = browser.css('.BlockOverallWrapper.table')
        self.assertEquals(1, len(blocks),
                          'Expected chapter to have exactly one block')
        block, = blocks

        self.assertEquals('The table has no content yet.'
                          ' Edit the table block for adding content.',
                          block.css('.portalMessage dd').first.text)

    @browsing
    def test_table_rendering(self, browser):
        create(Builder('table')
               .titled('The Table')
               .having(showTitle=True)
               .with_table([['Foo', 'Bar'],
                            ['1', '2'],
                            ['3', '4']])
               .within(self.chapter))

        browser.login().visit(self.chapter)
        block, = browser.css('.BlockOverallWrapper.table')

        self.assertEquals(
            [{'Foo': '1',
              'Bar': '2'},
             {'Foo': '3',
              'Bar': '4'}],
            block.css('table').first.dicts())

    @browsing
    def test_showing_block_title(self, browser):
        create(Builder('table')
               .titled('Visible')
               .with_dummy_table()
               .having(showTitle=True)
               .within(self.chapter))

        create(Builder('table')
               .titled('Hidden')
               .with_dummy_table()
               .having(showTitle=False)
               .within(self.chapter))

        browser.login().visit(self.chapter)
        visible, hidden = browser.css('.BlockOverallWrapper.table')

        self.assertEquals(
            ['Visible'],
            visible.css('table caption').text,
            'Expected block title of the "Visible" block to be visible.')

        self.assertEquals(
            [],
            hidden.css('table caption').text,
            'Expected block title of the "Hidden" block to be hidden.')

    @browsing
    def test_hidden_fields(self, browser):
        browser.login().open(self.chapter)
        factoriesmenu.add('Table')

        self.assertFalse(
            browser.find('Description'),
            '"Description" field should not be visible.')

        self.assertFalse(
            browser.find('Hide from table of contents'),
            '"Hide from table of contents" field should not be visible.')

        self.assertFalse(
            browser.find('Exclude from navigation'),
            '"Exclude from navigation" field should not be visible.')

    @browsing
    def test_latex_fields_available(self, browser):
        browser.login().open(self.chapter)
        factoriesmenu.add('Table')

        form = browser.find('Title').parent('form')
        labels = form.field_labels

        self.assertIn('LaTeX code above content', labels)
        self.assertIn('LaTeX code beneath content', labels)
