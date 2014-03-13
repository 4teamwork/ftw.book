from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
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

    @browsing
    def test_book_internal_links_are_marked_with_class(self, browser):
        book = create(Builder('book').titled('book'))
        chapter = create(Builder('chapter').within(book).titled('chapter'))

        html = '<a class="internal-link"' + \
            ' href="resolveuid/%s">' % IUUID(chapter) + \
            'The Chapter</a>'
        block = create(Builder('book textblock')
                       .within(chapter)
                       .having(text=html))

        reader_view = book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((block, book.REQUEST, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())

        link = browser.find('The Chapter')
        self.assertIn('book-internal', link.classes)
        self.assertDictContainsSubset(
            {'data-uid': IUUID(chapter)},
            link.attrib)

    @browsing
    def test_links_to_itself_are_not_marked_as_book_internal(self, browser):
        # Some titles are linked to the default view of the context
        # so that we can exit the reader and edit things.
        # Theese links should not be changed to pointing to the reader view.
        # One example is the title of chapters.

        book = create(Builder('book').titled('book'))
        chapter = create(Builder('chapter')
                         .within(book)
                         .titled('The Chapter'))

        reader_view = book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((chapter, book.REQUEST, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())

        link = browser.find('1 The Chapter')
        self.assertNotIn('book-internal', link.classes)
