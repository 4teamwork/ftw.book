from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing


def toc_tree(item=None):
    if not item:
        item = browser.css('#content-core ul.book-index > li').first
    return (item.css('>a').first.text,
            map(toc_tree, item.css('>ul>li')))


class TestBookView(FunctionalTestCase):

    @browsing
    def test_lists_table_of_contents(self, browser):
        browser.login().visit(self.example_book)

        toc = ('The Example Book',
               [('1 Introduction', [('1.1 Management Summary', [])]),
                ('2 Historical Background',
                 [('2.1 China', [('2.1.1 First things first', []),
                                 ('2.1.2 Important Documents', [])])]),
                ('3 Empty', [])])

        self.assertTupleEqual(toc, toc_tree())
