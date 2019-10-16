from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from StringIO import StringIO
from zipfile import ZipFile


class TestBookZipexport(FunctionalTestCase):

    @browsing
    def test_zipexport_integration(self, browser):
        browser.login().visit(self.example_book, view='zip_export')
        self.assertEquals('application/zip', browser.headers['Content-Type'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(
            ['the-example-book.pdf',
             'Historical Background/China/Important Documents/image.jpg',
             'Historical Background/China/Important Documents/lorem.html',
             'Empty/'],
            zipfile.namelist())
