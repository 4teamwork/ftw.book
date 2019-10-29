from Products.CMFCore.utils import getToolByName
from ftw.book.latex.defaultlayout import IDefaultBookLayout
from ftw.book.testing import LanguageSetter
from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
import re


def whitespace_clean_latex(latex):
    latex = re.sub('(\n) +', '\g<1>', latex)
    latex = re.sub('\n{3,}', '\n\n', latex)
    return latex


class TestDefaultBookLayout(FunctionalTestCase, LanguageSetter):

    def setUp(self):
        super(TestDefaultBookLayout, self).setUp()
        self.maxDiff = None

    def test_render_layout(self):
        layout = self.get_latex_layout(self.default_layout_book)
        self.assertMultiLineEqual(
            r'''
\def\sphinxdocclass{report}

\documentclass[letterpaper,10pt,english]{sphinxmanual}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{babel}
\usepackage{times}
\usepackage[Sonny]{fncychap}
\usepackage{longtable}
\usepackage{sphinx}

\DeclareUnicodeCharacter{00A0}{\nobreakspace}
\renewcommand{\familydefault}{\sfdefault}
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0em}
\renewcommand\releasename{Version}
\hypersetup{pdfborder=0 0 0}

\def\sphinxlogo{\includegraphics[width=.25\textwidth]{titlepage_logo.jpg}}

\title{The Default Layout Book}
\release{1.7.2}

\author{Mr. Smith}

\authoraddress{Smith Consulting\\
Swordstreet 1\\
1234 Anvil City}

\makeindex

\begin{document}

\maketitle

\tableofcontents
\clearpage

No content

\listoffigures

\listoftables

\renewcommand{\indexname}{Index}
\printindex

\end{document}
            '''.strip(),
            whitespace_clean_latex(layout.render_latex('No content')).strip())

    @browsing
    def test_layout_renders_with_defaults(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Book')
        browser.fill({'Title': 'The Book'}).submit()
        layout = self.get_latex_layout(browser.context)
        self.assertTrue(layout.render_latex('No content'))

    def test_index_title_translated_to_german(self):
        self.set_language_settings('de', ['de'])
        layout = self.get_latex_layout(self.default_layout_book)
        self.assertIn(
            r'\renewcommand{\indexname}{Stichwortverzeichnis}',
            whitespace_clean_latex(layout.render_latex('No content')).strip())

    def test_logo(self):
        layout = self.get_latex_layout(self.default_layout_book)
        def logo_latex():
            latex = whitespace_clean_latex(layout.render_latex('')).strip()
            lines =  filter(lambda line: line.startswith(r'\def\sphinxlogo'),
                            latex.splitlines())
            return '\n'.join(lines)

        self.assertEquals(
            r'\def\sphinxlogo{\includegraphics'
            r'[width=.25\textwidth]{titlepage_logo.jpg}}',
            logo_latex())

        IDefaultBookLayout(self.default_layout_book).titlepage_logo_width = 40
        self.assertEquals(
            r'\def\sphinxlogo{\includegraphics'
            r'[width=.40\textwidth]{titlepage_logo.jpg}}',
            logo_latex())

        IDefaultBookLayout(self.default_layout_book).titlepage_logo_width = 0
        self.assertEquals(
            r'\def\sphinxlogo{\includegraphics{titlepage_logo.jpg}}',
            logo_latex())

        IDefaultBookLayout(self.default_layout_book).titlepage_logo = None
        self.assertEquals(
            r'\def\sphinxlogo{}',
            logo_latex())
