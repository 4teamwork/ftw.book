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

    def test_render_toc(self):
        book_brain = self.create_dummy(
            getURL='/book',
            Title='Book')

        chapt_brain = self.create_dummy(
            getURL='/book/chapt',
            Title='Chapter')

        subchapt_brain = self.create_dummy(
            getURL='/book/chapt/subchapt',
            Title='Sub-Chapter')

        tree = {
            'item': book_brain,
            'toc_number': None,
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': chapt_brain,
                 'depth': 1,
                 'toc_number': '1',
                 'currentParent': False,
                 'currentItem': False,
                 'children': [

                        {'item': subchapt_brain,
                         'depth': 2,
                         'toc_number': '1.1',
                         'currentParent': False,
                         'currentItem': False,
                         'children': [

                                ]}

                        ]}

                ]}

        response = self.stub()
        self.expect(response.getHeader(ANY)).result('')
        self.expect(response.setHeader(ANY, ANY))

        request = self.stub()
        self.expect(request.debug).result(True)
        self.expect(request.response).result(response)

        self.replay()

        renderer = BookRenderer(object(), request, object())
        html = renderer.render_toc(tree)

        self.assertIn('<a href="/book">Book</a>', html)
        self.assertIn('<a href="/book/chapt">1 Chapter</a>', html)
        self.assertIn(
            '<a href="/book/chapt/subchapt">1.1 Sub-Chapter</a>', html)
