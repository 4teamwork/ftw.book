from ftw.book.interfaces import IBook
from ftw.book.tests import FunctionalTestCase


class TestBookAdapterReturnsBook(FunctionalTestCase):

    def test_on_book(self):
        self.assertEquals(self.example_book, IBook(self.example_book))

    def test_on_chapter(self):
        chapter = self.example_book.introduction
        self.assertEquals(self.example_book, IBook(chapter))

    def test_on_text_block(self):
        block = self.example_book.introduction.get('management-summary')
        self.assertEquals(self.example_book, IBook(block))
