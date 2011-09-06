from zope.interface import Interface


class IBook(Interface):
    """example book"""


class ILaTeXCodeInjectionEnabled(Interface):
    """Enables LaTeX code injection for admins on
    book-objects (chapters, SL-paragraphs).
    """
