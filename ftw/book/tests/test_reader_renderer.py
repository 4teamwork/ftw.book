from ftw.book.browser.reader.renderer import BookRenderer
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import provideAdapter
from zope.interface import Interface
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable


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

        self.replay()

        renderer = BookRenderer(context, request, object())
        html = renderer.render()
        self.assertIn('<h1>Book</h1>', html)
