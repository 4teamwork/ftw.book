from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.converter import BookHTML2LatexConverter
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyClass


class TestBookHTML2LatexConverter(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_component_is_registered(self):
        context = object()
        request = self.providing_stub([IWithinBookLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.expect(layout.use_package('soul'))

        self.replay()
        component = queryMultiAdapter((context, request, layout),
                                      IHTML2LaTeXConverter)

        self.assertNotEquals(component, None)
        self.assertEqual(type(component), BookHTML2LatexConverter)
        verifyClass(IHTML2LaTeXConverter, BookHTML2LatexConverter)

    def test_component_registered_only_within_book(self):
        context = object()
        request = object()
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()
        component = queryMultiAdapter((context, request, layout),
                                      IHTML2LaTeXConverter)

        self.assertNotEquals(component, None)
        self.assertNotEqual(type(component), BookHTML2LatexConverter)

    def test_converter_inherits_default_patterns(self):
        context = request = self.create_dummy()
        layout = self.stub()
        self.expect(layout.use_package(ANY))

        self.replay()

        conv = BookHTML2LatexConverter(context, request, layout)

        self.assertEqual(conv.convert('Hello <b>World</b>!'),
                         'Hello {\\bf World}!')

    def test_converter_converts_visualHighlight(self):
        context = request = self.create_dummy()
        layout = self.mocker.mock()
        self.expect(layout.use_package('soul'))

        self.replay()

        conv = BookHTML2LatexConverter(context, request, layout)

        self.assertEqual(
            conv.convert(r'foo <span class="visualHighlight">bar</span> baz'),
            r'foo \hl{bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span id="myid" class="visualHighlight">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span class="visualHighlight" id="myid">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span class="othercls visualHighlight">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span class="visualHighlight othercls">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span class="visualHighlight othercls">'
                         r'bar <b>BAR</b> bar</span> baz'),
            r'foo \hl{bar {\bf BAR} bar} baz')

        self.assertEqual(
            conv.convert(r'foo <span class="othercls" id="visualHighlight">'
                         r'bar</span> baz'),
            r'foo bar baz')
