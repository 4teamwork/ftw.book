from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestBookRenderer(TestCase):
    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_book_title_is_rendered(self, browser):
        book = create(Builder('book').titled('The Book'))
        reader_view = book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((book, book.REQUEST, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())
        self.assertEquals('The Book', browser.css('h1').first.text)


class TestBlockRenderer(TestCase):
    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_book_title_is_rendered(self, browser):
        book = create(Builder('book'))
        chapter = create(Builder('chapter').within(book))
        block = create(Builder('book textblock')
                       .within(chapter)
                       .having(text='<p>Some Text</p>'))

        reader_view = book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((block, book.REQUEST, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())
        self.assertEquals('Some Text', browser.css('p').first.text)
