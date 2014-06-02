from ftw.book.interfaces import IBook
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from unittest2 import TestCase


class TestBookAdapterReturnsBook(TestCase):
    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        self.book = create(Builder('book'))

    def test_on_book(self):
        self.assertEquals(self.book, IBook(self.book))

    def test_on_chapter(self):
        chapter = create(Builder('chapter').within(self.book))
        self.assertEquals(self.book, IBook(chapter))

    def test_on_text_block(self):
        chapter = create(Builder('chapter').within(self.book))
        block = create(Builder('book textblock').within(chapter))
        self.assertEquals(self.book, IBook(block))

    def test_on_file(self):
        chapter = create(Builder('chapter').within(self.book))
        block = create(Builder('file').within(chapter))
        self.assertEquals(self.book, IBook(block))
