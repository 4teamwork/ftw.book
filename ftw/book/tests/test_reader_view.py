from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.view import ReaderView
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase


class TestReaderView(MockTestCase):

    def test_get_book_obj(self):
        chapter = self.stub()
        book = self.providing_stub([IBook])
        self.set_parent(chapter, book)

        self.replay()

        view = ReaderView(chapter, object())

        self.assertEqual(view.get_book_obj(),
                         book)

    def test_get_book_obj_fails_when_there_is_no_book(self):
        context = self.set_parent(
            self.stub(),
            self.set_parent(
                self.stub(),
                self.providing_stub([IPloneSiteRoot])))

        self.replay()

        view = ReaderView(context, object())

        with self.assertRaises(Exception):
            view.get_book_obj()
