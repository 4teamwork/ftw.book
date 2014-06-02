from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.book.latex.listingblock import add_table_column_widths
from ftw.book.latex.listingblock import remove_html_links
from ftw.book.latex.listingblock import remove_table_summary
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.interfaces import IPDFAssembler
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestRemoveHTMLLinks(TestCase):

    def test_removes_links_from_html(self):
        html = 'foo <a /> bar'
        self.assertEquals('foo  bar', remove_html_links(html))

    def test_link_containments_are_kept(self):
        html = '<a>foo</a> bar'
        self.assertEquals('foo bar', remove_html_links(html))


class TestRemoveTableSummary(TestCase):

    def test_removes_table_summary_attribtue(self):
        html = '<table class="listing" summary="Foo"></table>'
        self.assertEquals('<table class="listing"></table>',
                          remove_table_summary(html))


class TestAddTableColumnWidths(TestCase):

    def test_adds_width_to_columns(self):
        input = '\n'.join((
                '<table><colgroup>',
                '<col class="col-modified" />',
                '<col class="col-Creator" />',
                '<col class="col-getObjSize" />',
                '<col />',
                '</colgroup></table>'))

        expected = ''.join((
                '<table><colgroup>',
                '<col class="col-modified" width="12%">',
                '<col class="col-Creator" width="15%">',
                '<col class="col-getObjSize" width="10%">',
                '<col width="63%">',
                '</colgroup></table>'))

        self.assertEquals(expected, add_table_column_widths(input))



class TestListingBlockLaTeXView(TestCase):

    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        self.book = create(Builder('book')
                           .with_layout(IDefaultBookLayoutSelectionLayer))
        self.chapter = create(Builder('chapter').within(self.book))

    def render_latex(self, obj):
        assembler = getMultiAdapter((self.book, obj.REQUEST), IPDFAssembler)
        view = getMultiAdapter((obj, obj.REQUEST, assembler.get_layout()),
                               ILaTeXView)
        return view.render()

    def test_title_is_shown_when_showTitle_enabled(self):
        listingblock = create(Builder('listingblock')
                              .titled('Files')
                              .having(showTitle=True)
                              .within(self.chapter))

        self.assertIn(r'\section{Files}', self.render_latex(listingblock))

    def test_title_is_not_shown_showTitle_disabled(self):
        listingblock = create(Builder('listingblock')
                              .titled('Files')
                              .having(showTitle=False)
                              .within(self.chapter))

        self.assertNotIn(r'Files', self.render_latex(listingblock))

    def test_title_not_in_table_of_contents(self):
        listingblock = create(Builder('listingblock')
                              .titled('Files')
                              .having(showTitle=True,
                                      hideFromTOC=True)
                              .within(self.chapter))

        self.assertIn(r'\section*{Files}', self.render_latex(listingblock))

    def test_table_lists_contents(self):
        listingblock = create(Builder('listingblock')
                              .having(showTitle=False)
                              .within(self.chapter))
        create(Builder('file').titled('The File').within(listingblock))

        latex = self.render_latex(listingblock)
        self.assertIn(r'\begin{tabular}', latex)
        self.assertIn(r'{The File}', latex)
