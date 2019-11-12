# -*- coding: utf-8 -*-

from ftw.book.latex.listingblock import add_table_column_widths
from ftw.book.latex.listingblock import remove_html_links
from ftw.book.latex.listingblock import remove_table_summary
from ftw.book.tests import FunctionalTestCase
from unittest import TestCase


class TestListingBlockLaTeXView(FunctionalTestCase):

    def test_standard_rendering(self):
        self.assert_latex_code(
            self.listingblock,
            r'''
\label{path:/plone/the-example-book/historical-background/china/important-documents}
\subsection{Important Documents}

\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
\setlength\tablewidth\linewidth
\addtolength\tablewidth{-4\tabcolsep}
\renewcommand{\arraystretch}{1.4}
\begin{tabular}{p{0.88\tablewidth}p{0.12\tablewidth}}
\hline
\multicolumn{1}{p{0.88\tablewidth}}{\textbf{Title}} & \multicolumn{1}{p{0.12\tablewidth}}{\textbf{modified}} \\
\hline
\multicolumn{1}{p{0.88\tablewidth}}{Einfache Webseite} & \multicolumn{1}{p{0.12\tablewidth}}{31.10.2016} \\
\hline
\multicolumn{1}{p{0.88\tablewidth}}{Fröhliches Bild} & \multicolumn{1}{p{0.12\tablewidth}}{31.10.2016} \\
\hline
\end{tabular}\\
\vspace{4pt}
            ''')

    def test_hide_title(self):
        self.listingblock.show_title = True
        with self.assert_latex_diff(
                self.listingblock,
                r'''
--- before.tex
+++ after.tex
@@ -1,6 +1,4 @@
 \label{path:/plone/the-example-book/historical-background/china/important-documents}
-\subsection{Important Documents}
-
 \makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
 \setlength\tablewidth\linewidth
 \addtolength\tablewidth{-4\tabcolsep}
                '''):
            self.listingblock.show_title = False

    def test_hide_title_from_toc(self):
        self.listingblock.hide_from_toc = False
        with self.assert_latex_diff(
                self.listingblock,
                r'''
--- before.tex
+++ after.tex
@@ -1,5 +1,5 @@
 \label{path:/plone/the-example-book/historical-background/china/important-documents}
-\subsection{Important Documents}
+\subsection*{Important Documents}

 \makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
 \setlength\tablewidth\linewidth
                '''):
            self.listingblock.hide_from_toc = True


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

        self.assertEquals(
            expected,
            add_table_column_widths(input).replace('\n', ''))
