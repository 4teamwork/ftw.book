from ftw.book.tests import FunctionalTestCase


class TestHTMLBlockLaTeXView(FunctionalTestCase):

    def test_default_latex(self):
        self.assert_latex_code(
            self.htmlblock,
            r'Some \textbf{bold} and \textit{italic} text.')

    def test_hide_title(self):
        self.htmlblock.show_title = True
        with self.assert_latex_diff(
                self.htmlblock,
                r'''
--- before.tex
+++ after.tex
@@ -1,3 +1 @@
-\section{An HTML Block}
-
 Some \textbf{bold} and \textit{italic} text.
                '''):
            self.htmlblock.show_title = False

    def test_hide_title_from_toc(self):
        self.htmlblock.show_title = True
        self.htmlblock.hide_from_toc = False
        with self.assert_latex_diff(
                self.htmlblock,
                r'''
--- before.tex
+++ after.tex
@@ -1,3 +1,3 @@
-\section{An HTML Block}
+\section*{An HTML Block}

 Some \textbf{bold} and \textit{italic} text.
                '''):
            self.htmlblock.hide_from_toc = True
