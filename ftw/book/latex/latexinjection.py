"""Contains a monkey patch patching LatexCTConverter.convertObject, so that
it includes pre- and post-latex code configured with ILaTeXCodeInjectionEnabled.
"""

from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from plonegov.pdflatex.browser.converter import LatexCTConverter
import logging


@staticmethod
def injection_aware_convertObject(view, object=None, brain=None):
    content_latex = LatexCTConverter._old_convertObject(view=view,
                                                        object=object,
                                                        brain=brain)

    if brain:
        obj = view.context.restrictedTraverse(brain.getPath())

    else:
        obj = object

    if not ILaTeXCodeInjectionEnabled.providedBy(obj):
        return content_latex

    latex = []

    pre_code = obj.getField('preLatexCode').get(obj)
    if pre_code:
        latex.append('')
        latex.append('%% ---- LaTeX pre code injection at %s' % '/'.join(
                obj.getPhysicalPath()))
        latex.append(pre_code)
        latex.append('%% ---- / LaTeX pre code injection')
        latex.append('')

    latex.append(content_latex)

    post_code = obj.getField('postLatexCode').get(obj)
    if post_code:
        latex.append('')
        latex.append('% ---- LaTeX post code injection at %s' % '/'.join(
                obj.getPhysicalPath()))
        latex.append(post_code)
        latex.append('% ---- / LaTeX post code injection')
        latex.append('')

    return '\n'.join(latex)


# monkey patch not done with collective.monkeypatcher since patching
# staticmethod is not supported.
logging.getLogger('ftw.book').info(
    'Monkeypatching LatexCTConverter.convertObject: '
    'adding ILaTeXCodeInjectionEnabled support')
LatexCTConverter._old_convertObject = staticmethod(LatexCTConverter.convertObject)
LatexCTConverter.convertObject = injection_aware_convertObject
