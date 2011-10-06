from zope.interface import Interface


class IBookReaderRenderer(Interface):
    """Adapter interface adapting:
    - a context
    - the request
    - the reader view

    Providing methods:

    - render: returns the HTML representation used in the reader view
    """

    def render(self):
        """Returns an HTML string, representing the adapted object in the
        book reader view.
        """
