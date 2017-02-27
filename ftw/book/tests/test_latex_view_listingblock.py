# -*- coding: utf-8 -*-

from ftw.book.tests import FunctionalTestCase
from plone.uuid.interfaces import IUUID


class TestListingBlockLaTeXView(FunctionalTestCase):

    def test_standard_rendering(self):
        self.assert_latex_code(
            self.listingblock,
            r'''
\subsection{Important Documents}

\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
\setlength\tablewidth\linewidth
\addtolength\tablewidth{-6\tabcolsep}
\renewcommand{\arraystretch}{1.4}
\begin{tabular}{p{0.44\tablewidth}p{0.44\tablewidth}p{0.12\tablewidth}}
\hline
\multicolumn{1}{p{0.44\tablewidth}}{\textbf{Type}} & \multicolumn{1}{p{0.44\tablewidth}}{\textbf{Title}} & \multicolumn{1}{p{0.12\tablewidth}}{\textbf{modified}} \\
\hline
\multicolumn{1}{p{0.44\tablewidth}}{} & \multicolumn{1}{p{0.44\tablewidth}}{Einfache Webseite} & \multicolumn{1}{p{0.12\tablewidth}}{27.02.2017} \\
\hline
\multicolumn{1}{p{0.44\tablewidth}}{} & \multicolumn{1}{p{0.44\tablewidth}}{Fröhliches Bild} & \multicolumn{1}{p{0.12\tablewidth}}{27.02.2017} \\
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
@@ -1,5 +1,3 @@
-\subsection{Important Documents}
-
 \makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
 \setlength\tablewidth\linewidth
 \addtolength\tablewidth{-6\tabcolsep}
                '''):
            self.listingblock.show_title = False

    def test_hide_title_from_toc(self):
        self.listingblock.hide_from_toc = False
        with self.assert_latex_diff(
                self.listingblock,
                r'''
--- before.tex
+++ after.tex
@@ -1,4 +1,4 @@
-\subsection{Important Documents}
+\subsection*{Important Documents}

 \makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
 \setlength\tablewidth\linewidth
                '''):
            self.listingblock.hide_from_toc = True
