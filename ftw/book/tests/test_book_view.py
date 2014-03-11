from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from unittest2 import TestCase


def toc_tree(item=None):
    if not item:
        item = browser.css('#content-core ul > li').first
    return (item.css('>div').first.text,
            map(toc_tree, item.css('>ul>li')))


class TestBookView(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_lists_table_of_contents(self, browser):
        book = create(Builder('book').titled('The Book'))
        chapter = create(Builder('chapter').titled('First Chapter')
                         .within(book))
        subchapter = create(Builder('chapter').titled('The SubChapter')
                            .within(chapter))
        create(Builder('book textblock').titled('Hidden Title Block')
               .having(showTitle=False).within(subchapter))
        create(Builder('book textblock').titled('Visible Title Block')
               .having(showTitle=True).within(subchapter))
        create(Builder('chapter').titled('Second Chapter').within(book))

        browser.login().visit(book)

        toc = ('The Book', [
                ('1 First Chapter', [
                        ('1.1 The SubChapter', [
                                ('1.1.1 Visible Title Block', [])])]),
                ('2 Second Chapter', [])])

        self.assertTupleEqual(toc, toc_tree())
