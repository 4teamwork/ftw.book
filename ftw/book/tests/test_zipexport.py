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
        self.folder = create(Builder('folder'))

        self.book = create(Builder('book').titled('The Book')
                           .within(self.folder))
        chapter1 = create(Builder('chapter').titled('First Chapter')
                          .within(self.book))

        listingblock1 = create(Builder('listingblock').within(chapter1))
        create(Builder('image').titled('The Image 1').within(listingblock1)
               .with_dummy_content())

        subchapter = create(Builder('chapter').titled('The SubChapter')
                            .within(chapter1))
        create(Builder('book textblock').titled('Hidden Title Block')
               .having(showTitle=False).within(subchapter))
        create(Builder('book textblock').titled('Visible Title Block')
               .having(showTitle=True).within(subchapter))

        listingblock2 = create(Builder('listingblock').within(subchapter))
        create(Builder('image').titled('The Image 2').within(listingblock2)
               .with_dummy_content())

        chapter2 = create(Builder('chapter').titled('Second Chapter')
                          .within(self.book))

        listingblock3 = create(Builder('listingblock').within(chapter2))
        create(Builder('image').titled('The Image 3').within(listingblock3)
               .with_dummy_content())

    @browsing
    def test_zipexport_integration(self, browser):
        browser.login().visit(self.folder, view='zip_export')

        self.assertEquals('application/zip', browser.headers['Content-Type'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(
            ['the-book.pdf',
             'The Book/First Chapter/image.gif',
             'The Book/First Chapter/The SubChapter/image.gif',
             'The Book/Second Chapter/image.gif'],
            zipfile.namelist())
