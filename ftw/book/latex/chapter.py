from ftw.book.helpers import BookHelper
from ftw.book.interfaces import IChapter
from ftw.book.latex import utils
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapts
from zope.interface import Interface


class ChapterLaTeXView(RecursiveLaTeXView):
    adapts(IChapter, Interface, Interface)

    def render(self):
        latex = self.get_heading_counters_latex()
        latex += utils.get_latex_heading(self.context, self.layout)
        latex += self.render_children()
        return latex

    def get_heading_counters_latex(self):
        if self.context != self.layout.context:
            # Only set the heading counters when exporting this chapter
            # directly. Otherwise it is not the first content.
            return ''

        counters = (
            'chapter',
            'section',
            'subsection',
            'subsubsection',
            'paragraph',
            'subparagraph',
            )

        helper = BookHelper()
        heading_numbers = helper.get_chapter_level(self.context)
        latex = []

        if heading_numbers[-1] == 1:
            del heading_numbers[-1]
        else:
            heading_numbers[-1] -= 1

        for level, num in enumerate(heading_numbers):
            latex.append(r'\setcounter{%s}{%s}' % (
                    counters[level], num))

        if latex:
            latex.append('')

        return '\n'.join(latex)
