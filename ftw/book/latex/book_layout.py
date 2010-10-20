from ftw.book.interfaces import IBook


class BookLayout(object):

    def __call__(self, view, context):
        self.view = view
        self.context = context
        self.setDocumentClass()
        self.registerPackages()
        self.appendHeadCommands()
        self.appendAboveBodyCommands()
        self.appendBeneathBodyCommands()
    #def getResourceFileData(self, filename, resource='ftw.book.latex.resource'):
        #fiveFile = self.context.restrictedTraverse(
        #    '++resource++%s/%s' % (resource, filename))
        #path = fiveFile.context.path
        #fileData = open(path).read()
        #return fileData
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
