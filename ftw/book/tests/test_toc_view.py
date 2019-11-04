from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestTOCView(FunctionalTestCase):

    @browsing
    def test_toc_depth_config(self, browser):
        browser.login().visit(self.example_book)

        # view shows all subchapters by default
        self.assertEquals(
            [
                'The Example Book',
                '1 Introduction',
                '1.1 Management Summary',
                '2 Historical Background',
                '2.1 China',
                '2.1.1 First things first',
                '2.1.2 Important Documents',
                '3 Empty',
            ],
            [e.text for e in browser.css('#content-core .book-index a')])

        # limit depth to 1 subchapter
        browser.open(self.example_book, view='edit')
        browser.fill({'Table of contents depth': '1'}).submit()

        self.assertEquals(
            [
                'The Example Book',
                '1 Introduction',
                '2 Historical Background',
                '3 Empty',
            ],
            [e.text for e in browser.css('#content-core .book-index a')])

        # limit depth to 2 subchapter
        browser.open(self.example_book, view='edit')
        browser.fill({'Table of contents depth': '2'}).submit()

        # view shows all subchapters by default
        self.assertEquals(
            [
                'The Example Book',
                '1 Introduction',
                '1.1 Management Summary',
                '2 Historical Background',
                '2.1 China',
                '3 Empty',
            ],
            [e.text for e in browser.css('#content-core .book-index a')])

        # empty depth means no limit
        browser.open(self.example_book, view='edit')
        browser.fill({'Table of contents depth': '0'}).submit()

        self.assertEquals(
            [
                'The Example Book',
                '1 Introduction',
                '1.1 Management Summary',
                '2 Historical Background',
                '2.1 China',
                '2.1.1 First things first',
                '2.1.2 Important Documents',
                '3 Empty',
            ],
            [e.text for e in browser.css('#content-core .book-index a')])
