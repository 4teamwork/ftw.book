"""Adds pre- and post-latex-views for every object within a book,
mixing in the additional preLatexCode and postLatexCode.
"""

from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import IWithinBookLayer
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import adapts
from zope.interface import Interface


class InjectionLaTeXViewBase(MakoLaTeXView):

    def get_rendered_latex_for(self, fieldname):
        field = self.context.Schema().getField(fieldname)

        # in some cases the field can not be retrieved.
        if not field:
            return ''

        code = field.get(self.context)
        if not code:
            return ''

        latex = [
            '',
            '%% ---- LaTeX injection (%s) at %s' % (
                fieldname,
                '/'.join(self.context.getPhysicalPath())),
            code,
            '%% ---- end LaTeX injection (%s)' % fieldname
            ]

        return '\n'.join(latex)


class PreInjectionLaTeXView(InjectionLaTeXViewBase):
    """Mixes in the preLatexCode for every object providing
    ILaTeXCodeInjectionEnabled and within a book.
    """

    adapts(ILaTeXCodeInjectionEnabled, IWithinBookLayer, Interface)

    def render(self):
        return self.get_rendered_latex_for('preLatexCode')


class PostInjectionLaTeXView(InjectionLaTeXViewBase):
    """Mixes in the postLatexCode for every object providing
    ILaTeXCodeInjectionEnabled and within a book.
    """

    adapts(ILaTeXCodeInjectionEnabled, IWithinBookLayer, Interface)

    def render(self):
        return self.get_rendered_latex_for('postLatexCode')
