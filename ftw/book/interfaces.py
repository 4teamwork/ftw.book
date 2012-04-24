from simplelayout.types.common.interfaces import IPage
from zope.interface import Interface


class IBook(Interface):
    """Book marker interface.
    """


class IChapter(IPage):
    """Chapter marker interface.
    """


class IHTMLBlock(Interface):
    """HTMLBlock marker interface.
    """


class IRemark(Interface):
    """Remark marker interface.
    """


class ITable(Interface):
    """Remark marker interface.
    """


class IAddRemarkLayer(Interface):
    """ Request layer interface, provided if we select to show remarks in
    the pdf export wizard
    """


class IWithinBookLayer(Interface):
    """Request layer interface, automatically provided by request
    when traversing over book.
    """


class ILaTeXCodeInjectionEnabled(Interface):
    """Enables LaTeX code injection for admins on
    book-objects (chapters, SL-paragraphs).
    """
