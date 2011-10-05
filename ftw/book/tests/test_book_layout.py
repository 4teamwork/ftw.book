from ftw.book.interfaces import IBook
from ftw.book.latex.book_layout import BookLayout
from mocker import ANY
from plone.mocktestcase import MockTestCase
from plonegov.pdflatex.browser.aspdf import AsPDFView
from plonegov.pdflatex.converter import html2latex
from zope.interface import directlyProvides


class TestBookLayout(MockTestCase):

    def test_title_page(self):
        book = self.create_dummy(use_titlepage=True,
                                 use_toc=False)
        directlyProvides(book, IBook)

        view = self.mocker.mock(AsPDFView)
        self.expect(view.appendToProperty('latex_above_body',
                                          r'\maketitle'))

        self.replay()

        layout = BookLayout()
        layout.view = view
        layout.context = book

        layout.appendAboveBodyCommands()

    def test_table_of_contents(self):
        book = self.create_dummy(use_titlepage=False,
                                 use_toc=True)
        directlyProvides(book, IBook)

        view = self.mocker.mock(AsPDFView)
        self.expect(view.appendToProperty('latex_above_body',
                                          r'\tableofcontents'))
        self.expect(view.appendToProperty('latex_above_body',
                                          r'\clearpage'))

        self.replay()

        layout = BookLayout()
        layout.view = view
        layout.context = book

        layout.appendAboveBodyCommands()

    def test_list_of_images(self):
        book = self.create_dummy(use_loi=True,
                                 use_lot=False)
        directlyProvides(book, IBook)

        view = self.mocker.mock(AsPDFView)
        self.expect(view.appendToProperty('latex_beneath_body',
                                          r'\listoffigures'))

        self.replay()

        layout = BookLayout()
        layout.view = view
        layout.context = book

        layout.appendBeneathBodyCommands()

    def test_list_of_tables(self):
        book = self.create_dummy(use_loi=False,
                                 use_lot=True)
        directlyProvides(book, IBook)

        view = self.mocker.mock(AsPDFView)
        self.expect(view.appendToProperty('latex_beneath_body',
                                          r'\listoftables'))

        self.replay()

        layout = BookLayout()
        layout.view = view
        layout.context = book

        layout.appendBeneathBodyCommands()

    def test_visual_highlight_custom_html2latex_rule(self):
        view = self.mocker.mock(AsPDFView)

        self.expect(view.registerPackage('soul'))

        self.expect(view.html2latex_converter._insertCustomPattern((
                    html2latex.MODE_REGEXP,
                    r'<span.*?class="visualHighlight">(.*?)</span>',
                    r'\\hl{\g<1>}')))

        self.replay()

        layout = BookLayout()
        layout.view = view

        layout.register_html2latex_rules()

    def test_no_titlepage_and_lists_in_no_book_content(self):
        obj = self.create_dummy()

        view = self.mocker.mock(AsPDFView)

        self.replay()

        layout = BookLayout()
        layout.view = view
        layout.context = obj

        # we expect that nothing is done, since the context does not provide
        # IBook. If something would be done on the view, the mocker would
        # raise an unmet expression.
        layout.appendAboveBodyCommands()
        layout.appendBeneathBodyCommands()

    def test_full_layout(self):
        book = self.create_dummy(
            pagestyle='twoside',
            Title=lambda: 'My Book',
            use_titlepage=True,
            use_toc=True,
            use_loi=True,
            use_lot=True)
        directlyProvides(book, IBook)

        view = self.mocker.mock(AsPDFView)

        # custom html2latex rules are tested in a test above
        view.registerPackage('soul')
        self.expect(view.html2latex_converter._insertCustomPattern(
                ANY)).count(0, None)

        # document class
        view.setLatexProperty('document_class', 'book')
        view.setLatexProperty('document_config',
                              'a4paper,12pt,german,twoside')

        # default packages
        view.registerPackage('inputenc', 'utf8')
        view.registerPackage('fontenc', 'T1')
        view.registerPackage('babel', 'ngerman')
        view.registerPackage('geometry',
                             'left=25mm,right=45mm,top=23mm,bottom=30mm')
        view.registerPackage('xcolor')
        view.registerPackage('graphicx')
        view.registerPackage('textcomp')
        view.registerPackage('helvet')
        view.registerPackage('hyperref')

        # font
        view.appendHeaderCommand(
            r'\renewcommand{\familydefault}{\sfdefault}')

        # title
        view.appendHeaderCommand(r'\title{My Book}')

        # titlepage, toc, loi, lot
        view.appendToProperty('latex_above_body', r'\maketitle')
        view.appendToProperty('latex_above_body', r'\tableofcontents')
        view.appendToProperty('latex_above_body', r'\clearpage')
        view.appendToProperty('latex_beneath_body', r'\listoffigures')
        view.appendToProperty('latex_beneath_body', r'\listoftables')

        self.replay()

        BookLayout()(view, book)

