from ftw.book.interfaces import IBook
from ftw.book.latex.defaultlayout import DefaultBookLayout
from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface.verify import verifyClass


class TestDefaultBookLayout(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def _mock_book(self, data=None):
        options = {
            'Title': 'My book',
            'getUse_titlepage': True,
            'getUse_toc': True,
            'getUse_lot': True,
            'getUse_loi': True,
            'author_address': 'Bern\nSwitzerland',
            'release': '2.5',
            'author': '4teamwork',
            'titlepage_logo': None,
            'titlepage_width': 0,
            }

        if data:
            options.update(data)

        if options.get('titlepage_logo', None):
            options['titlepage_logo'] = self.create_dummy(
                data=options['titlepage_logo'])

        book = self.providing_stub([IBook])
        for key, value in options.items():
            self.expect(getattr(book, key)()).result(value)

        for key in ['author_address', 'author', 'release', 'titlepage_logo',
                    'titlepage_logo_width']:
            value = options.get(key)
            self.expect(book.Schema().getField(key).get(book)).result(value)

        return book
        
    def _mock_portal_languages_tool(self):
        language_tool = self.mocker.mock()
        self.mock_tool(language_tool, 'portal_languages')
        self.expect(language_tool.getPreferredLanguage()).result('en')

    def test_component_is_registered(self):
        context = object()
        request = self.providing_stub([IDefaultBookLayoutSelectionLayer])
        builder = self.providing_stub([IBuilder])

        self.replay()
        component = getMultiAdapter((context, request, builder),
                                    ILaTeXLayout)

        self.assertNotEquals(component, None)
        self.assertEqual(type(component), DefaultBookLayout)

    def test_layout_only_registered_within_book(self):
        context = object()
        request = self.providing_stub([IDefaultBookLayoutSelectionLayer])
        builder = object()

        self.replay()
        component = queryMultiAdapter((context, request, builder),
                                    ILaTeXLayout)

        self.assertEqual(component, None)

    def test_layout_implements_interface(self):
        self.assertTrue(ILaTeXLayout.implementedBy(DefaultBookLayout))
        verifyClass(ILaTeXLayout, DefaultBookLayout)

    def test_get_book_walks_up(self):
        book = self.providing_stub([IBook])
        subchapter = self.set_parent(
            self.stub(), self.set_parent(
                self.stub(),
                book))

        self.replay()

        layout = DefaultBookLayout(subchapter, object(), object())

        self.assertEqual(layout.get_book(), book)

    def test_get_book_returns_None_if_not_within_book(self):
        root = self.stub()
        self.expect(root.__parent__, None)
        obj = self.set_parent(
            self.stub(),
            self.set_parent(
                self.stub(),
                root))

        self.replay()
        layout = DefaultBookLayout(obj, object(), object())

        self.assertEqual(layout.get_book(), None)

    def test_get_render_arguments(self):
        self._mock_portal_languages_tool()
        book = self._mock_book()
        self.replay()

        layout = DefaultBookLayout(book, object(), object())

        self.assertEqual(
            layout.get_render_arguments(),
            {'context_is_book': True,
             'title': 'My book',
             'use_titlepage': True,
             'use_toc': True,
             'use_lot': True,
             'use_loi': True,
             'authoraddress': r'Bern\\Switzerland',
             'author': '4teamwork',
             'release': '2.5',
             'babel': 'english',
             'logo': False,
             'logo_width': 0})
             
    def test_get_render_arguments_babel(self):
        book = self._mock_book()

        language_tool = self.mocker.mock()
        self.mock_tool(language_tool, 'portal_languages')
        self.expect(language_tool.getPreferredLanguage()).result('de')

        self.replay()

        layout = DefaultBookLayout(book, object(), object())

        self.assertEqual(layout.get_render_arguments()['babel'], 'ngerman')

    def test_rendering_works(self):
        self._mock_portal_languages_tool()
        book = self._mock_book()
        builder = self.mocker.mock()

        self.expect(builder.add_file('sphinx.sty', data=ANY))
        self.expect(builder.add_file('fncychap.sty', data=ANY))
        self.expect(builder.add_file('sphinxftw.cls', data=ANY))
        self.expect(builder.add_file('sphinxhowto.cls', data=ANY))
        self.expect(builder.add_file('sphinxmanual.cls', data=ANY))
        self.replay()

        layout = DefaultBookLayout(book, object(), builder)

        latex = layout.render_latex('content latex')

        self.assertIn(r'My book', latex)
        self.assertIn(r'content latex', latex)
        self.assertIn(r'\maketitle', latex)
        self.assertIn(r'\tableofcontents', latex)
        self.assertIn(r'\listoffigures', latex)
        self.assertIn(r'\listoftables', latex)
        self.assertIn(r'\release{2.5}', latex)
        self.assertIn(r'\author{4teamwork}', latex)
        self.assertIn(r'\authoraddress{Bern\\Switzerland}', latex)

    def test_disabled_metadata(self):
        self._mock_portal_languages_tool()
        book = self._mock_book({
                'release': '',
                'author': '',
                'author_address': ''})
        builder = self.mocker.mock()

        self.expect(builder.add_file('sphinx.sty', data=ANY))
        self.expect(builder.add_file('fncychap.sty', data=ANY))
        self.expect(builder.add_file('sphinxftw.cls', data=ANY))
        self.expect(builder.add_file('sphinxhowto.cls', data=ANY))
        self.expect(builder.add_file('sphinxmanual.cls', data=ANY))
        self.replay()

        layout = DefaultBookLayout(book, object(), builder)

        latex = layout.render_latex('content latex')

        self.assertNotIn(r'\release{', latex)
        self.assertNotIn(r'\author', latex)
        self.assertNotIn(r'\authoraddress', latex)

    def test_logo_with_width(self):
        self._mock_portal_languages_tool()
        book = self._mock_book({
                'titlepage_logo': 'my-image',
                'titlepage_logo_width': 55})
        builder = self.mocker.mock()

        self.expect(builder.add_file('titlepage_logo.jpg', data='my-image'))

        self.expect(builder.add_file('sphinx.sty', data=ANY))
        self.expect(builder.add_file('fncychap.sty', data=ANY))
        self.expect(builder.add_file('sphinxftw.cls', data=ANY))
        self.expect(builder.add_file('sphinxhowto.cls', data=ANY))
        self.expect(builder.add_file('sphinxmanual.cls', data=ANY))
        self.replay()

        layout = DefaultBookLayout(book, object(), builder)

        latex = layout.render_latex('content latex')

        self.assertIn(
            r'\def\sphinxlogo{\includegraphics[width=.55\textwidth]{' + \
                r'titlepage_logo.jpg}}',
            latex)

    def test_logo_without_width(self):
        self._mock_portal_languages_tool()
        book = self._mock_book({
                'titlepage_logo': 'my-image',
                'titlepage_logo_width': 0})
        builder = self.mocker.mock()

        self.expect(builder.add_file('titlepage_logo.jpg', data='my-image'))

        self.expect(builder.add_file('sphinx.sty', data=ANY))
        self.expect(builder.add_file('fncychap.sty', data=ANY))
        self.expect(builder.add_file('sphinxftw.cls', data=ANY))
        self.expect(builder.add_file('sphinxhowto.cls', data=ANY))
        self.expect(builder.add_file('sphinxmanual.cls', data=ANY))
        self.replay()

        layout = DefaultBookLayout(book, object(), builder)

        latex = layout.render_latex('content latex')

        self.assertIn(
            r'\def\sphinxlogo{\includegraphics{' + \
                r'titlepage_logo.jpg}}',
            latex)
