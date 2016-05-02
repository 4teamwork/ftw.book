from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestTOCView(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_toc_depth_config(self, browser):
        book = create(Builder('book').titled('The Book'))
        chapter = create(Builder('chapter')
                         .titled('First Chapter')
                         .within(book))
        subchapter = create(Builder('chapter')
                            .titled('The SubChapter')
                            .within(chapter))
        create(Builder('chapter')
               .titled('The SubSubChapter')
               .within(subchapter))

        browser.login().visit(book)

        # view shows all subchapters by default
        self.assertEquals(
            ['The Book', '1 First Chapter',
                '1.1 The SubChapter', '1.1.1 The SubSubChapter'],
            [e.text for e in browser.css('#content-core .navTreeItem a')])

        # limit depth to 1 subchapter
        browser.open(book, view='edit')
        browser.fill({'Table of contents depth': '1'}).submit()

        self.assertEquals(
            ['The Book', '1 First Chapter'],
            [e.text for e in browser.css('#content-core .navTreeItem a')])

        # limit depth to 2 subchapter
        browser.open(book, view='edit')
        browser.fill({'Table of contents depth': '2'}).submit()

        self.assertEquals(
            ['The Book', '1 First Chapter', '1.1 The SubChapter'],
            [e.text for e in browser.css('#content-core .navTreeItem a')])

        # empty depth means no limit
        browser.open(book, view='edit')
        browser.fill({'Table of contents depth': ''}).submit()

        self.assertEquals(
            ['The Book', '1 First Chapter',
                '1.1 The SubChapter', '1.1.1 The SubSubChapter'],
            [e.text for e in browser.css('#content-core .navTreeItem a')])
