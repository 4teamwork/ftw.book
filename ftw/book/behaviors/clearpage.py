from ftw.book import _
from ftw.book.permissions import MODIFY_LATEX_INJECTION_PERMISSION
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import fieldset
from plone.supermodel.model import Schema
from zope.interface import provider
from zope.schema import Bool


@provider(IFormFieldProvider)
class IClearpage(Schema):

    fieldset(
        'latex',
        label=_(u'LaTeX'),
        fields=(
            'pre_latex_clearpage',
            'post_latex_clearpage',
        ))

    write_permission(pre_latex_clearpage=MODIFY_LATEX_INJECTION_PERMISSION)
    pre_latex_clearpage = Bool(
        title=_(u'injection_label_insert_clearpage_before_content',
                default=u'Insert page break before this content'),
        required=False,
        default=False)

    write_permission(post_latex_clearpage=MODIFY_LATEX_INJECTION_PERMISSION)
    post_latex_clearpage = Bool(
        title=_(u'injection_label_insert_clearpage_after_content',
                default=u'Insert page break after this content'),
        required=False,
        default=False)
