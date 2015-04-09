from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase
from zipfile import ZipFile
from StringIO import StringIO


class TestBookZipexport(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book').titled('The Book'))
        chapter = create(Builder('chapter').titled('First Chapter')
                         .within(self.book))
        subchapter = create(Builder('chapter').titled('The SubChapter')
                            .within(chapter))
        create(Builder('book textblock').titled('Hidden Title Block')
               .having(showTitle=False).within(subchapter))
        create(Builder('book textblock').titled('Visible Title Block')
               .having(showTitle=True).within(subchapter))
        create(Builder('chapter').titled('Second Chapter').within(self.book))

    @browsing
    def test_zipexport_integration(self, browser):
        browser.login().visit(self.book, view='zip_export')

        self.assertEquals('application/zip', browser.headers['Content-Type'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(['the-book.pdf'], zipfile.namelist())
