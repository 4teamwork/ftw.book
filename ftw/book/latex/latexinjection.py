"""Adds pre- and post-latex-views for every object within a book,
mixing in the additional preLatexCode and postLatexCode.
"""

from ftw.book.behaviors.clearpage import IClearpage
from ftw.book.behaviors.codeinjection import ILaTeXCodeInjection
from ftw.book.behaviors.columnlayout import IChangeColumnLayout
from ftw.book.behaviors.landscape import ILandscape
from ftw.book.interfaces import IBookContentType
from ftw.book.interfaces import ILaTeXInjectionController
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(ILaTeXLayout, Interface)
@implementer(ILaTeXInjectionController)
class LaTeXInjectionController(object):

    ANNOTATION_KEY = 'latex-injection-controller'

    def __init__(self, layout, request):
        self.layout = layout
        self.request = request
        self._storage = None

    def get_current_layout(self):
        return self._get_storage().get('current_layout', ONECOLUMN_LAYOUT)

    def set_layout(self, layout):
        if not layout or layout not in (ONECOLUMN_LAYOUT, TWOCOLUMN_LAYOUT):
            return ''

        if layout is self.get_current_layout():
            return ''

        self._get_storage()['current_layout'] = layout
        if layout == ONECOLUMN_LAYOUT:
            return r'\onecolumn'

        elif layout == TWOCOLUMN_LAYOUT:
            return r'\twocolumn'

        else:
            return ''

    def is_landscape(self):
        return self._get_storage().get('landscape_enabled', False)

    def set_landscape(self, obj, enabled):
        if not enabled or self.is_landscape():
            return r''

        self.layout.use_package('lscape')

        storage = self._get_storage()
        storage['landscape_enabled'] = True
        storage['landscape_closing_object'] = obj

        return r'\begin{landscape}'

    def close_landscape(self, obj):
        if not self.is_landscape():
            return r''

        storage = self._get_storage()
        if storage.get('landscape_closing_object', None) == obj:
            storage['landscape_enabled'] = False
            storage['landscape_closing_object'] = None
            return r'\end{landscape}'

        else:
            return r''

    def _get_storage(self):
        if self._storage is None:
            ann = IAnnotations(self.layout)
            key = self.__class__.ANNOTATION_KEY
            if key not in ann:
                ann[key] = {}
            self._storage = ann[key]
        return self._storage


class InjectionLaTeXViewBase(MakoLaTeXView):

    def get_rendered_latex_for(self, schema, fieldname):
        code = self.get_field_value(schema, fieldname)
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

    def get_field_value(self, schema, fieldname):
        return getattr(schema(self.context, None), fieldname, None)

    def get_controller(self):
        return getMultiAdapter((self.layout, self.request),
                               ILaTeXInjectionController)


@adapter(IBookContentType, Interface, Interface)
class PreInjectionLaTeXView(InjectionLaTeXViewBase):

    def render(self):
        latex = []

        self.layout.use_package('hyperref')
        path = '/'.join(self.context.getPhysicalPath())
        latex.append(r'\label{path:%s}' % path)

        if self.get_field_value(IClearpage, 'pre_latex_clearpage'):
            latex.append(r'\clearpage')

        if self.get_field_value(IChangeColumnLayout, 'pre_latex_newpage'):
            latex.append(r'\newpage')

        latex.append(self._render_preferred_layout())
        latex.append(self._render_landscape())
        latex.append(self.get_rendered_latex_for(ILaTeXCodeInjection,
                                                 'pre_latex_code'))

        return '\n'.join(filter(None, latex)).strip()

    def _render_landscape(self):
        landscape = self.get_field_value(ILandscape, 'landscape')
        controller = self.get_controller()
        return controller.set_landscape(self.context, landscape)

    def _render_preferred_layout(self):
        preferred_layout = self.get_field_value(
            IChangeColumnLayout, 'preferred_column_layout')
        controller = self.get_controller()
        return controller.set_layout(preferred_layout)


@adapter(IBookContentType, Interface, Interface)
class PostInjectionLaTeXView(InjectionLaTeXViewBase):

    def render(self):
        latex = []

        if self.get_field_value(IClearpage, 'post_latex_clearpage'):
            latex.append(r'\clearpage')

        latex.append(self._render_landscape())
        latex.append(self.get_rendered_latex_for(ILaTeXCodeInjection,
                                                 'post_latex_code'))

        return '\n'.join(filter(None, latex)).strip()

    def _render_landscape(self):
        controller = self.get_controller()
        return controller.close_landscape(self.context)
