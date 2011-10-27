from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.interfaces import IBook
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.component import adapts
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IBrowserView


class BaseBookReaderRenderer(object):
    """Base block renderer used to subclass.
    """

    implements(IBookReaderRenderer)

    def __init__(self, context, request, readerview):
        self.context = context
        self.request = request
        self.readerview = readerview


class DefaultBlockRenderer(BaseBookReaderRenderer):
    """The simplelayout block renderer.
    It renders the simplealyout default "block_view".
    """

    adapts(ISimpleLayoutBlock, Interface, IBrowserView)

    def render(self):
        view = self.context.restrictedTraverse('block_view')
        return view()


class BookRenderer(BaseBookReaderRenderer):
    """The book renderer renders the title page and the table of
    contents of the book.
    """

    adapts(IBook, Interface, IBrowserView)

    template = ViewPageTemplateFile('templates/book_title.pt')

    def render(self):
        return self.template(title=self.context.Title())
