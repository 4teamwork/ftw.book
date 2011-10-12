from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.interfaces import IBook
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
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

    toc_template = ViewPageTemplateFile('templates/toc_recurse.pt')

    def render(self):
        html = []

        if self.context.getUse_toc():
            html.append(self.render_toc())

        return '\n'.join(html)

    def render_toc(self, item=None):
        if item is None:
            item = self.readerview.get_toc_tree(self.readerview.tree)

        toc_title = item.get('item').Title

        if item.get('toc_number', None):
            toc_title = '%s %s' % (item.get('toc_number'), toc_title)

        return self.toc_template(**{
                'item': item,
                'is_root': item.get('depth', -1) == 0,
                'li_class': 'book-toc-%s' % str(item.get('depth')),
                'toc_title': toc_title})
