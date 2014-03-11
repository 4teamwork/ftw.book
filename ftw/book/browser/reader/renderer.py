from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from StringIO import StringIO
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.interfaces import IBook
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.component import adapts
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IBrowserView
import lxml.html


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
        html = view()
        html = self.mark_book_internal_links(html)
        return html

    def mark_book_internal_links(self, html):
        book = IBook(self.context)
        book_url = book.absolute_url()
        book_path = '/'.join(book.getPhysicalPath())
        context_url = self.context.absolute_url()

        doc = lxml.html.parse(StringIO(html))
        for node in doc.xpath('//a'):
            if 'href' not in node.attrib:
                continue

            if node.attrib['href'] == context_url:
                continue

            path = node.attrib['href'].replace(book_url, book_path)
            uid = self.get_uid_by_path(path)
            if uid is None:
                continue

            if 'class' in node.attrib:
                node.attrib['class'] += ' book-internal'
            else:
                node.attrib['class'] = 'book-internal'

            node.attrib['data-uid'] = uid

        return lxml.html.tostring(doc)

    def get_uid_by_path(self, path):
        catalog = getToolByName(self.context, 'portal_catalog')
        rid = catalog.getrid(path)
        if rid is None:
            return None

        metadata = catalog.getMetadataForRID(rid)
        return metadata.get('UID', None)


class BookRenderer(BaseBookReaderRenderer):
    """The book renderer renders the title page and the table of
    contents of the book.
    """

    adapts(IBook, Interface, IBrowserView)

    template = ViewPageTemplateFile('templates/book_title.pt')

    def render(self):
        return self.template(title=self.context.Title())
