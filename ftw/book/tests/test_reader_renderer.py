from ftw.book.browser.reader.renderer import BookRenderer
from ftw.testing import MockTestCase
from mocker import ANY


class TestBookRenderer(MockTestCase):

    def test_render_toc(self):
        tree = {
            'item': {'getURL': '/book',
                     'Title': 'Book'},
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': {'getURL': '/book/chapt',
                          'Title': 'Chapter'},
                 'depth': 1,
                 'currentParent': False,
                 'currentItem': False,
                 'children': [

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
        self.assertIn('<a href="/book/chapt">Chapter</a>', html)
