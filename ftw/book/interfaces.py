from zope.interface import Interface


class IBook(Interface):
    """example book"""


class IWithinBookLayer(Interface):
    """Request layer interface, automatically provided by request
    when traversing over book.
    """


class ILaTeXCodeInjectionEnabled(Interface):
    """Enables LaTeX code injection for admins on
    book-objects (chapters, SL-paragraphs).
    """
