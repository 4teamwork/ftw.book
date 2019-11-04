# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from ftw.simplelayout.contenttypes.contents.interfaces import IFileListingBlock
from ftw.simplelayout.contenttypes.contents.interfaces import ITextBlock
from zope.interface import Interface


ModifyLaTeXInjection = "ftw.book: Modify LaTeX Injection"


class IBookContentType(Interface):
    """All ftw.book content types provide this interface.
    """


class IBook(IBookContentType):
    """Book marker interface.
    """


class IChapter(IBookContentType):
    """Chapter marker interface.
    """


class IHTMLBlock(IBookContentType):
    """HTMLBlock marker interface.
    """


class ITable(IBookContentType):
    """Table marker interface.
    """


class IBookTextBlock(ITextBlock, IBookContentType):
    """Book text block marker interface.
    """


class IBookFileListingBlock(IFileListingBlock, IBookContentType):
    """File listing block for books.
    """


class IBookLayoutBehavior(Interface):
    """Mark a behavior as a book layout behavior so that it appears in
    the layout selection vocabulary and acts as instance behavior.
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
