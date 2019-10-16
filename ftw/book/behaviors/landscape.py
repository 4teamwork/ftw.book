from ftw.book import _
from ftw.book.permissions import MODIFY_LATEX_INJECTION_PERMISSION
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import fieldset
from plone.supermodel.model import Schema
from zope.interface import provider
from zope.schema import Bool


@provider(IFormFieldProvider)
class ILandscape(Schema):

    fieldset(
        'latex',
        label=_(u'LaTeX'),
        fields=(
            'landscape',
        ))

    write_permission(landscape=MODIFY_LATEX_INJECTION_PERMISSION)
    landscape = Bool(
        title=_(u'injection_label_landscape', default=u'Use landscape'),
        required=False,
        default=False)
