from ftw.book.interfaces import IBook
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.layouts import DefaultBookLayout
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface.verify import verifyClass


class TestDefaultBookLayout(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def _mock_book(self):
        book = self.providing_stub([IBook])
        self.expect(book.Title()).result('My book')
        self.expect(book.getUse_titlepage()).result(True)
        self.expect(book.getUse_toc()).result(True)
        self.expect(book.getUse_lot()).result(True)
        self.expect(book.getUse_loi()).result(True)
        return book

    def test_component_is_registered(self):
        context = object()
        request = self.providing_stub([IWithinBookLayer])
        builder = self.providing_stub([IBuilder])

        self.replay()
        component = getMultiAdapter((context, request, builder),
                                    ILaTeXLayout)

        self.assertNotEquals(component, None)
        self.assertEqual(type(component), DefaultBookLayout)

    def test_layout_only_registered_within_book(self):
        context = object()
        request = self.providing_stub([IWithinBookLayer])
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
             'use_loi': True})

    def test_rendering_works(self):
        book = self._mock_book()
        builder = self.mocker.mock()

        self.expect(builder.add_file('sphinx.sty', data=ANY))
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
