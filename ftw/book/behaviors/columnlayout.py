from ftw.book import _
from ftw.book.interfaces import NO_PREFERRED_LAYOUT
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from ftw.book.permissions import MODIFY_LATEX_INJECTION_PERMISSION
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import fieldset
from plone.supermodel.model import Schema
from zope.interface import provider
from zope.schema import Bool
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


PREFERRED_COLUMN_LAYOUT_VOCABULARY = SimpleVocabulary((
    SimpleTerm(value=NO_PREFERRED_LAYOUT,
               title=_('injection_label_no_preferred_column_layout',
                       default='No preferred column layout')),
    SimpleTerm(value=ONECOLUMN_LAYOUT,
               title=_('injection_label_one_column_layout',
                       default='One column layout')),
    SimpleTerm(value=TWOCOLUMN_LAYOUT,
               title=_('injection_label_two_column_layout',
                       default='Two column layout')),
))


@provider(IFormFieldProvider)
class IChangeColumnLayout(Schema):

    fieldset(
        'latex',
        label=_(u'LaTeX'),
        fields=(
            'preferred_column_layout',
            'pre_latex_newpage',
        ))

    write_permission(preferred_column_layout=MODIFY_LATEX_INJECTION_PERMISSION)
    preferred_column_layout = Choice(
        title=_(u'injection_label_preferred_column_layout',
                default=u'Preferred layout'),
        description=_(
            u'injection_help_preferred_column_layout',
            default=u'When choosing a one or two column layout, the '
            u'layout will switched for this content and all '
            u'subsequent contents in the PDF, if necessary. '
            u'If "no preferred layout" is selected the currently '
            u'active layout is kept.'),
        required=False,
        default=NO_PREFERRED_LAYOUT,
        vocabulary=PREFERRED_COLUMN_LAYOUT_VOCABULARY)

    write_permission(pre_latex_newpage=MODIFY_LATEX_INJECTION_PERMISSION)
    pre_latex_newpage = Bool(
        title=_(u'injection_label_insert_newpage_before_content',
                default=u'Insert column break before this content'),
        description=_(u'This option inserts a column break when '
                      u'two column layout is active.'))
