from ftw.book.browser.reader import renderer
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.testing import MockTestCase
from mocker import ANY
from simplelayout.base.interfaces import ISimpleLayoutBlock
from unittest2 import TestCase
from zope.component import provideAdapter, adaptedBy
from zope.interface import Interface
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable


class TestBaseBookReaderRenderer(TestCase):

    def test_implements(self):
        self.assertTrue(IBookReaderRenderer.implementedBy(
                renderer.BaseBookReaderRenderer))

    def test_init_sets_attributes(self):
        context = object()
        request = object()
        readerview = object()

        obj = renderer.BaseBookReaderRenderer(
            context, request, readerview)

        self.assertEqual(obj.context, context)
        self.assertEqual(obj.request, request)
        self.assertEqual(obj.readerview, readerview)


class TestDefaultBlcokRenderer(MockTestCase):

    def test_component(self):
        self.assertTrue(IBookReaderRenderer.implementedBy(
                renderer.DefaultBlockRenderer))

        adapt_interfaces = adaptedBy(renderer.DefaultBlockRenderer)
        self.assertEqual(adapt_interfaces[0], ISimpleLayoutBlock)

    def test_render_renders_sl_block(self):
        context = self.stub()
        self.expect(context.restrictedTraverse('block_view')()).result(
            'sl block html')

        self.replay()

        obj = renderer.DefaultBlockRenderer(context, object(), object())
        self.assertEqual(obj.render(), 'sl block html')


class TestBookRenderer(MockTestCase):

    def setUp(self):
        # Page templates use the traversing mechainsm for accessing
        # attributes on objects, so we need to register the default
        # traversable adapter.
        provideAdapter(factory=DefaultTraversable,
                       adapts=[Interface],
                       provides=ITraversable)

    def test_book_render(self):
        response = self.stub()
        self.expect(response.getHeader(ANY)).result('')
        self.expect(response.setHeader(ANY, ANY))

        request = self.stub()
        self.expect(request.debug).result(True)
        self.expect(request.response).result(response)

        context = self.stub()
        self.expect(context.Title()).result('Book')
        self.expect(context.__parent__).result(None)

        self.replay()

        obj = renderer.BookRenderer(context, request, object())
        html = obj.render()
        self.assertIn('<h1>Book</h1>', html)
