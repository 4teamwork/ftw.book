from Acquisition import aq_chain
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.interfaces import IBook
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from StringIO import StringIO
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import lxml.html


@implementer(IBookReaderRenderer)
class BaseBookReaderRenderer(object):

    def __init__(self, context, request, readerview):
        self.context = context
        self.request = request
        self.readerview = readerview


@adapter(ISimplelayoutBlock, Interface, IBrowserView)
class DefaultBlockRenderer(BaseBookReaderRenderer):

    def render(self):
        view = self.context.restrictedTraverse('block_view')
        html = view(prepend_html_headings=True)
        html = self.mark_book_internal_links(html)
        return html

    def mark_book_internal_links(self, html):
        books = filter(IBook.providedBy, aq_chain(self.context))
        if not books:
            raise ValueError('Not within book.')
        book = books[0]
        book_url = book.absolute_url()
        book_path = '/'.join(book.getPhysicalPath())
        context_url = self.context.absolute_url()

        doc = lxml.html.parse(StringIO(u'<div>{}</div>'.format(html)))
        for node in doc.xpath('//a'):
            if 'href' not in node.attrib:
                continue

            url = self.resolve_uid(node.attrib['href'])
            if url == context_url:
                continue

            path = url.replace(book_url, book_path)
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

    def resolve_uid(self, url):
        if '/' not in url:
            return url

        parts = url.split('/')
        if parts[-2] == 'resolveuid' or parts[-2] == 'resolveUid':
            reference_catalog = getToolByName(self.context,
                                              'reference_catalog')

            uid = parts[-1]
            obj = reference_catalog.lookupObject(uid)

            if obj is not None:
                url = obj.absolute_url()
        return url


@adapter(IBook, Interface, IBrowserView)
class BookRenderer(BaseBookReaderRenderer):
    template = ViewPageTemplateFile('templates/book_title.pt')

    def render(self):
        return self.template(title=self.context.Title())
