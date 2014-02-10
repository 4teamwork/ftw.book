from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestBookNavigation(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_portlet_is_crated_when_book_is_crated(self, browser):
        folder = create(Builder('folder').titled('The Folder'))
        book = create(Builder('book').titled('The Book').within(folder))
        create(Builder('chapter').titled('The Chapter').within(book))

        browser.login().visit(book)
        self.assertEquals(
            ['The Book', 'The Chapter'],
            browser.css('.portletNavigationTree .navTreeItem').text)
