from ftw.book.behaviors.toc import IHideTitleFromTOC
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create


class TestHTMLBlockLaTeXView(FunctionalTestCase):

    def test(self):
        block = create(Builder('book htmlblock')
                       .having(show_title=False,
                               content=u'foo <b>bar</b> baz').
                       within(self.example_book.empty))

        self.assertEquals(
            'foo \\textbf{bar} baz\n',
            self.get_latex_view_for(block).render())

        block.title = u'A Fancy HTML Block'
        block.show_title = True
        self.assertEquals(
            '\\section{A Fancy HTML Block}\n\n'
            'foo \\textbf{bar} baz\n',
            self.get_latex_view_for(block).render())

        IHideTitleFromTOC(block).hide_from_toc = True
        self.assertEquals(
            '\\section*{A Fancy HTML Block}\n\n'
            'foo \\textbf{bar} baz\n',
            self.get_latex_view_for(block).render())

        block.content = None
        self.assertEquals(
            '\\section*{A Fancy HTML Block}\n\n',
            self.get_latex_view_for(block).render())
