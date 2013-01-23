from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.highlight_subconverter import VisualHighlightSubconverter
from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from zope.component import adapts
from zope.interface import implements, Interface


BOTTOM = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM


class BookHTML2LatexConverter(HTML2LatexConverter):
    implements(interfaces.IHTML2LaTeXConverter)
    adapts(Interface, IWithinBookLayer, interfaces.ILaTeXLayout)

    def __init__(self, context, request, layout):
        HTML2LatexConverter.__init__(self, context, request, layout)

        custom_patterns = []

        for num in range(1, 7):
            custom_patterns.append(
                (interfaces.HTML2LATEX_MODE_REGEXP,
                 r'<h%s.*?>(.*?)</h%s>' % (num, num),
                 r'{\\bf \g<1>}'))

        self.register_patterns(custom_patterns)

        # We should never use "= within a \\hl{}
        self._insert_custom_pattern(
            (interfaces.HTML2LATEX_MODE_REGEXP,
             r'\\hl{(.*?)"=(.*?)}',
             r'\hl{\g<1>-\g<2>}',
             interfaces.HTML2LATEX_REPEAT_MODIFIER),
            placeholder=BOTTOM)

        # Cleanup empty \hl{} (whitespace and \\)
        self._insert_custom_pattern(
            (interfaces.HTML2LATEX_MODE_REGEXP,
             r'\\hl{[\s\\]*}',
             r'',
             interfaces.HTML2LATEX_REPEAT_MODIFIER),
            placeholder=BOTTOM)


    def get_default_subconverters(self):
        converters = list(HTML2LatexConverter.get_default_subconverters(self))
        converters.append(VisualHighlightSubconverter)
        return converters
