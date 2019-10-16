from ftw.book.interfaces import IChapter
from ftw.book.latex import utils
from ftw.book.toc import TableOfContents
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.view import RecursiveLaTeXView
from zope.component import adapter
from zope.interface import Interface


@adapter(IChapter, Interface, ILaTeXLayout)
class ChapterLaTeXView(RecursiveLaTeXView):

    def render(self):
        latex = self.get_heading_counters_latex()
        latex += utils.get_latex_heading(self.context, self.layout)
        latex += self.render_children()
        return latex

    def get_heading_counters_latex(self):
        if self.context != getattr(self.layout, 'export_context', None):
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

        toc = TableOfContents()
        heading_numbers = map(toc.index, toc.parent_chapters(self.context))
        heading_numbers.append(toc.index(self.context) - 1)

        latex = []
        for level, num in enumerate(heading_numbers):
            latex.append(r'\setcounter{%s}{%s}' % (
                    counters[level], num))

        if latex:
            latex.append('')

        return '\n'.join(latex)
