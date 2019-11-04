from ftw.book import _
from ftw.book.permissions import MODIFY_LATEX_INJECTION_PERMISSION
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import fieldset
from plone.supermodel.model import Schema
from zope.interface import provider
from zope.schema import Text


@provider(IFormFieldProvider)
class ILaTeXCodeInjection(Schema):

    fieldset(
        'latex',
        label=_(u'LaTeX'),
        fields=(
            'pre_latex_code',
            'post_latex_code',
        ))

    write_permission(pre_latex_code=MODIFY_LATEX_INJECTION_PERMISSION)
    pre_latex_code = Text(
        title=_(u'pre_latex_code_label',
                default=u'LaTeX code above content'),
        description=_(u'pre_latex_code_help', default=u''),
        required=False)

    write_permission(post_latex_code=MODIFY_LATEX_INJECTION_PERMISSION)
    post_latex_code = Text(
        title=_(u'post_latex_code_label',
                default=u'LaTeX code beneath content'),
        description=_(u'post_latex_code_help', default=u''),
        required=False)
