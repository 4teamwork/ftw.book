from ftw.book.interfaces import ITable
from ftw.book.latex.table import TableLaTeXView
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.interface import alsoProvides, Interface
from zope.interface.verify import verifyClass


class TestTableLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        layout_obj = self.create_dummy()
        alsoProvides(layout_obj, ILaTeXLayout)
        self.converter = getMultiAdapter((object(), object(), layout_obj),
                                         IHTML2LaTeXConverter)

    def test_component_is_registered(self):
        context = self.providing_stub([ITable])
        request = self.providing_stub([Interface])
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(type(view), TableLaTeXView)

    def test_component_implements_interface(self):
        self.assertTrue(ILaTeXView.implementedBy(TableLaTeXView))
        verifyClass(ILaTeXView, TableLaTeXView)


    def test_rendering(self):
        context = self.providing_stub([ITable])
        self.expect(context.getTable()).result('table')
        self.expect(context.getFootnoteText().strip()).result(
            'foot <b>note</b>')

        request = self.providing_stub([Interface])
        layout = self.providing_stub([ILaTeXLayout])

        self.expect(layout.get_converter()).result(self.converter)

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(view.render(),
            'table\n\\vspace{0pt}\n{\\footnotesize foot {\\bf note}}'
        )
