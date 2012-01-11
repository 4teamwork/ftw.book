from ftw.book.interfaces import IWithinBookLayer
from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from zope.component import adapts
from zope.interface import implements, Interface


class BookHTML2LatexConverter(HTML2LatexConverter):
    implements(interfaces.IHTML2LaTeXConverter)
    adapts(Interface, IWithinBookLayer, interfaces.ILaTeXLayout)

    def __init__(self, context, request, layout):
        HTML2LatexConverter.__init__(self, context, request, layout)

        custom_patterns = [
            # requires package "soul", included in book_layout
            (interfaces.HTML2LATEX_MODE_REGEXP,
             r'<span.*?class="[^=]*?visualHighlight[^"]*"[^>]*>(.*?)</span>',
             r'\\hl{\g<1>}'),
            ]

        self.register_patterns(custom_patterns)

        self.layout.use_package('soul')
