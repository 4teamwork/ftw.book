from ftw.book.interfaces import IBook
from plonegov.pdflatex.converter import html2latex


class BookLayout(object):

    def __call__(self, view, context):
        self.view = view
        self.context = context
        self.register_html2latex_rules()
        self.setDocumentClass()
        self.registerPackages()
        self.appendHeadCommands()
        self.appendAboveBodyCommands()
        self.appendBeneathBodyCommands()

    def register_html2latex_rules(self):
        """Registers custom html2latex rules
        """

        self.view.registerPackage('soul')

        customMap = [
            # requires package "soul", included in book_layout
            (html2latex.MODE_REGEXP,
             r'<span.*?class="visualHighlight">(.*?)</span>',
             r'\\hl{\g<1>}'),
            ]

        for customPattern in customMap:
            self.view.html2latex_converter._insertCustomPattern(customPattern)

    def setDocumentClass(self):
        self.view.setLatexProperty('document_class', 'book')
        self.view.setLatexProperty('document_config',
            'a4paper,12pt,german,%s' % self.context.pagestyle)

    def registerPackages(self):
        self.view.registerPackage('inputenc', 'utf8')
        self.view.registerPackage('fontenc', 'T1')
        self.view.registerPackage('babel', 'ngerman')
        self.view.registerPackage('geometry',
            'left=25mm,right=45mm,top=23mm,bottom=30mm')
        self.view.registerPackage('xcolor')
        self.view.registerPackage('graphicx')
        self.view.registerPackage('textcomp')
        self.view.registerPackage('helvet')
        self.view.registerPackage('hyperref')

    def appendHeadCommands(self):
        self.view.appendHeaderCommand(r'\renewcommand{\familydefault}{\sfdefault}')
        self.view.appendHeaderCommand("\\title{%s}"%(self.context.Title()))

    def appendAboveBodyCommands(self):
        if IBook.providedBy(self.context):
            if self.context.use_titlepage:
                self.view.appendToProperty('latex_above_body', "\\maketitle")
            if self.context.use_toc:
                self.view.appendToProperty('latex_above_body',
                    "\\tableofcontents")
                self.view.appendToProperty('latex_above_body', "\\clearpage")

    def appendBeneathBodyCommands(self):
        if IBook.providedBy(self.context):
            if self.context.use_loi:
                self.view.appendToProperty('latex_beneath_body',
                    "\\listoffigures")
            if self.context.use_lot:
                self.view.appendToProperty('latex_beneath_body',
                    "\\listoftables")
