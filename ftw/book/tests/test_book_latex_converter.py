from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.converter import BookHTML2LatexConverter
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyClass
import tempfile


class TestBookHTML2LatexConverter(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_component_is_registered(self):
        context = object()
        request = self.providing_stub([IWithinBookLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.expect(layout.use_package('soulutf8'))

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
                         'Hello \\textbf{World}!')


class TestBookConverterVisualHighlight(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def mock_visual_highlight(self, count):
        super(TestBookConverterVisualHighlight, self).setUp()

        context = request = self.create_dummy()
        layout = self.mocker.mock()

        self.expect(layout.use_package(
                'soulutf8')).count(count)

        builder = self.mocker.mock()
        self.expect(layout.get_builder()).result(builder).count(
            count, None)

        self.expect(builder.build_directory).result(
            tempfile.gettempdir()).count(count, None)

        self.expect(builder.add_file(
                'soulutf8.sty', ANY)).count(count)
        self.expect(builder.add_file(
                'infwarerr.sty', ANY)).count(count)
        self.expect(builder.add_file(
                'etexcmds.sty', ANY)).count(count)

        self.replay()

        self.convert = BookHTML2LatexConverter(
            context, request, layout).convert

    def test_simple_visual_highlight(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span class="visualHighlight">bar</span> baz'),
            r'foo \hl{bar} baz')

    def test_multiple_visual_highlight(self):
        self.mock_visual_highlight(2)
        self.assertEqual(
            self.convert(r'foo <span class="visualHighlight">bar</span> '
                         r'<span class="visualHighlight">baz</span> !'),
            r'foo \hl{bar} \hl{baz} !')

    def test_visual_highlight_with_other_args(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span id="myid" class="visualHighlight">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

    def test_visual_highlight_with_other_args2(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span class="visualHighlight" id="myid">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

    def test_visual_highlight_with_other_classes(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span class="othercls visualHighlight">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

    def test_visual_highlight_with_other_classes2(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span class="visualHighlight othercls">'
                         r'bar</span> baz'),
            r'foo \hl{bar} baz')

    def test_visual_highlight_with_bold(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'foo <span class="visualHighlight othercls">'
                         r'bar <b>BAR</b> bar</span> baz'),
            r'foo \hl{bar \textbf{BAR} bar} baz')

    def test_non_visual_highlight(self):
        self.mock_visual_highlight(0)
        self.assertEqual(
            self.convert(r'foo <span class="othercls" id="visualHighlight">'
                         r'bar</span> baz'),
            r'foo bar baz')

    def test_visual_highlight_with_hyphens(self):
        # no "= in \hl allowed
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(r'one <span class="visualHighlight">two-three-four'
                         r'</span> five-six'),
            r'one \hl{two-three-four} five"=six')

    def test_no_empty_visual_highlight(self):
        self.mock_visual_highlight(1)  # is added and then removed
        self.assertEqual(
            self.convert(
                r'foo <span class="visualHighlight"></span> bar'),
            r'foo  bar')

    def test_no_empty_visual_highlight2(self):
        self.mock_visual_highlight(1)  # is added and then removed
        self.assertEqual(
            self.convert(
                r'foo <span class="visualHighlight"> <br /></span> bar'),
            r'foo  bar')

    def test_no_empty_visual_highlight3(self):
        self.mock_visual_highlight(1)  # is added and then removed
        self.assertEqual(
            self.convert(
                r'foo <span class="visualHighlight"><br /> </span>bar'),
            r'foo bar')

    def test_no_nested_visual_highlight(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(
                r'<p style="text-align: justify; ">'
                r'<span class="visualHighlight">foo bar.<br />'
                r'<span class="visualHighlight">baz</span></span></p>'),
            '\\hl{foo bar.\\\\\nbaz}')

    def test_no_nested_visual_highlight2(self):
        self.mock_visual_highlight(1)
        self.assertEqual(
            self.convert(
                r'<p style="text-align: justify; ">'
                r'<span class="visualHighlight">foo bar.<br />'
                r'<span class="visualHighlight">baz.'
                r'<span class="visualHighlight"> <br /></span></span>'
                r'</span></p>'),
            '\\hl{foo bar.\\\\\nbaz. \\\\\n}')
