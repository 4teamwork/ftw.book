from ftw.book.interfaces import IWithinBookLayer
from ftw.book.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from simplelayout.base.interfaces import ISimpleViewletProvider
from simplelayout.types.common.interfaces import IParagraph
from zope.browser.interfaces import IBrowserView
from zope.component import getMultiAdapter
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.viewlet.interfaces import IViewlet


class TestTableValidationViewlet(MockTestCase):

    layer = ZCML_LAYER

    def create_stubs(self, text):
        context = self.providing_stub([IParagraph])
        self.expect(context.getText()).result(text)

        request = self.stub_request([IWithinBookLayer,
                                     IUserPreferredLanguages])
        self.expect(request.getPreferredLanguages()).result('en')

        view = self.providing_stub(IBrowserView)
        manager = self.providing_stub([ISimpleViewletProvider])
        return context, request, view, manager

    def test_invisible_when_valid(self):
        stubs = self.create_stubs('Hello World')
        self.replay()

        viewlet = getMultiAdapter(stubs, IViewlet,
            name='ftw.book.paragraph.validation')

        viewlet.update()
        self.assertEqual(viewlet.render().strip(), '')

    def test_validates_table_width(self):
        html = '\n'.join((
                '<table>',
                '<tr>',
                '<td>foo</td>',
                '</tr>',
                '</table>'))

        stubs = self.create_stubs(html)
        self.replay()

        viewlet = getMultiAdapter(stubs, IViewlet,
            name='ftw.book.paragraph.validation')

        viewlet.update()
        viewlet_html = viewlet.render().strip()

        self.assertIn(
            'Please specify the width of the table columns / cells.',
            viewlet_html)

    def test_validates_multiple_table_widths(self):
        html = '\n'.join((
                '<table>',
                '<tr><td width="100%">foo</td></tr>',
                '</table>',
                'bar',
                '<table>',
                '<tr><td>bar</td></tr>',
                '</table>'))

        stubs = self.create_stubs(html)
        self.replay()

        viewlet = getMultiAdapter(stubs, IViewlet,
            name='ftw.book.paragraph.validation')

        viewlet.update()
        viewlet_html = viewlet.render().strip()

        self.assertIn(
            'Please specify the width of the table columns / cells.',
            viewlet_html)
