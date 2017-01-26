from ftw.book import _
from ftw.book.permissions import MODIFY_LATEX_INJECTION_PERMISSION
from plone.autoform.directives import order_after
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel.model import Schema
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Bool


@provider(IFormFieldProvider)
class IHideTitleFromTOC(Schema):

    write_permission(hide_from_toc=MODIFY_LATEX_INJECTION_PERMISSION)
    order_after(hide_from_toc='show_title')
    hide_from_toc = Bool(
        title=_(u'injection_label_hide_from_toc',
                default=u'Hide from table of contents'),
        description=_(u'injection_help_hide_from_toc',
                      default=u'Hides the title from the table of '
                      u'contents and does not number the heading.'),
        required=False,
        default=False,
        missing_value=False)


class IShowInToc(Interface):
    """Show in table of contents.
    """
