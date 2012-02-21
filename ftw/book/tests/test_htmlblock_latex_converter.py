from ftw.book.interfaces import IBook
from ftw.book.interfaces import IHTMLBlock
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.htmlblock import HTMLBlockLaTeXView
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass


class TestHTMLBlockLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        layout_obj = self.create_dummy()
        alsoProvides(layout_obj, ILaTeXLayout)
        self.converter = getMultiAdapter((object(), object(), layout_obj),
                                         IHTML2LaTeXConverter)

    def test_component_is_registered(self):
        context = self.providing_stub([IHTMLBlock])
        request = self.providing_stub([IWithinBookLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(type(view), HTMLBlockLaTeXView)

    def test_component_implements_interface(self):
        self.assertTrue(ILaTeXView.implementedBy(HTMLBlockLaTeXView))
        verifyClass(ILaTeXView, HTMLBlockLaTeXView)

    def test_rendering_without_title(self):
        context = self.providing_stub([IHTMLBlock])
        self.expect(context.getShowTitle()).result(False)
        self.expect(context.getText()).result('foo <b>bar</b> baz')

        request = self.providing_stub([IWithinBookLayer])

        layout = self.providing_stub([ILaTeXLayout])
        self.expect(layout.get_converter()).result(self.converter)

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(view.render(), 'foo {\\bf bar} baz\n')

    def test_rendering_with_title(self):
        block = self.providing_stub([IHTMLBlock])
        self.expect(block.getShowTitle()).result(True)
        self.expect(block.pretty_title_or_id()).result(
            'My <b>HTML</b> block')
        self.expect(block.getText()).result('bar <b>foo</b> baz')

        book = self.providing_stub([IBook])
        self.set_parent(block, book)

        request = self.providing_stub([IWithinBookLayer])

        layout = self.providing_stub([ILaTeXLayout])
        self.expect(layout.get_converter()).result(self.converter)

        self.replay()

        view = queryMultiAdapter((block, request, layout),
                                 ILaTeXView)

        latex = view.render()

        self.assertIn(r'\chapter{My {\bf HTML} block}', latex)
        self.assertIn(r'bar {\bf foo} baz', latex)
