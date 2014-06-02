from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from unittest2 import TestCase



class TestChapter(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book'))

    @browsing
    def test_creating_chapter(self, browser):
        browser.login().visit(self.book)
        factoriesmenu.add('Chapter')

        browser.fill({'Title': 'The Chapter'}).submit()
        self.assertEquals(self.book.absolute_url() + '/the-chapter/view',
                          browser.url)
        self.assertEquals('The Chapter', browser.css('h1').first.text)

    @browsing
    def test_subchapter_is_rendered_as_block_in_parent(self, browser):
        chapter = create(Builder('chapter')
                         .titled('Chapter')
                         .within(self.book))

        subchapter = create(Builder('chapter')
                            .titled('Sub Chapter')
                            .within(chapter))

        browser.login().visit(chapter)
        block, = browser.css('.BlockOverallWrapper.chapter')
        self.assertEquals(['1.1 Sub Chapter'], block.css('h3').text)

        block.find('1.1 Sub Chapter').click()
        self.assertEquals(subchapter, browser.context)
