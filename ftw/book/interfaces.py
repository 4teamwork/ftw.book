# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface


ModifyLaTeXInjection = "ftw.book: Modify LaTeX Injection"


class IBook(Interface):
    """Book marker interface.
    """


class IChapter(Interface):
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


class IBookTextBlock(Interface):
    """Book text block marker interface.
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
    book-objects (chapters, text blocks).
    """


class ILaTeXInjectionController(Interface):
    """This adapter controlls LaTeX injection and providing methods for
    retrieving the current injection state, such as the current column
    layout.
    """

    def __init__(layout, request):
        """Adapts an ``ILaTeXLayout``. The current state is stored as
        annotation on the layout.
        """

    def get_current_layout():
        """Returns the current layout. This is one of:

        - ``ftw.book.interfaces.NO_PREFERRED_LAYOUT``
        - ``ftw.book.interfaces.ONECOLUMN_LAYOUT``
        - ``ftw.book.interfaces.TWOCOLUMN_LAYOUT``
        """

    def set_layout(layout):
        """Sets the current layout to one of:

        - ``ftw.book.interfaces.NO_PREFERRED_LAYOUT``
        - ``ftw.book.interfaces.ONECOLUMN_LAYOUT``
        - ``ftw.book.interfaces.TWOCOLUMN_LAYOUT``

        Returns the LaTeX code to be embedded for applying the
        layout changes, if necessary.
        """

    def is_landscape():
        """Returns ``True`` if the previous content was rendered in landscape
        mode.
        """

    def set_landscape(obj, enabled):
        """Set the landscape mode for an object and returns LaTeX code to
        be inserted before the content of the object.
        """

    def close_landscape(obj):
        """Returns LaTeX code to be inserted after the contents of the obj,
        if necessary.
        """


NO_PREFERRED_LAYOUT = u''
ONECOLUMN_LAYOUT = u'onecolumn'
TWOCOLUMN_LAYOUT = u'twocolumn'
