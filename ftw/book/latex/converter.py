from ftw.book.interfaces import IBookContentType
from ftw.book.latex.highlight_subconverter import VisualHighlightSubconverter
from ftw.book.latex.hyperlink_subconverter import BookHyperlinkConverter
from ftw.book.latex.index_subconverter import IndexSubconverter
from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverters import hyperlink
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


BOTTOM = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM


@implementer(interfaces.IHTML2LaTeXConverter)
@adapter(IBookContentType, Interface, interfaces.ILaTeXLayout)
class BookHTML2LatexConverter(HTML2LatexConverter):

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

        # Convert <span class="keyword"> tags into
        # <keyword> tags with the same meaning.
        # The <keyword> tags are converted later by the
        # IndexSubconverter.
        self._insert_custom_pattern(
            (interfaces.HTML2LATEX_MODE_REGEXP,
             r'<span ([^>]*)class="[^"]*keyword[^"]*"([^>]*)>(.*?)</span>',
             r'\g<3><keyword \g<1>\g<2>/>'),
            placeholder=interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP)

    def get_default_subconverters(self):
        converters = list(HTML2LatexConverter.get_default_subconverters(self))
        converters.append(VisualHighlightSubconverter)
        converters.append(IndexSubconverter)

        converters[converters.index(hyperlink.HyperlinkConverter)] = \
            BookHyperlinkConverter
        return converters
