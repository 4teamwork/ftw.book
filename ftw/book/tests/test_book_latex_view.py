from ftw.book.interfaces import IBook
from ftw.book.latex.book import BookLaTeXView
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter


class TestBookLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_returns_rendered_children_latex(self):
        context = self.providing_mock([IBook])
        request = self.mocker.mock()
        layout = self.mocker.mock()

        self.expect(layout.context).result(context)
        self.expect(request.get('paths', None)).result(None)

        child1 = self.mocker.mock()
        child2 = self.mocker.mock()
        self.expect(context.listFolderContents()).result([child1, child2])

        self.expect(layout.render_latex_for(child1)).result(
            'child one latex')
        self.expect(layout.render_latex_for(child2)).result(
            'child two latex')

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)
        self.assertTrue(isinstance(view, BookLaTeXView))

        self.assertEqual(
            view.render(),
            'child one latex\nchild two latex')
