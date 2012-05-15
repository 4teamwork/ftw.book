from ftw.book.interfaces import IRemark, IAddRemarkLayer
from ftw.book.latex.remark import RemarkLaTeXView
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass


class TestRemarkLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        layout_obj = self.create_dummy()
        alsoProvides(layout_obj, ILaTeXLayout)
        self.converter = getMultiAdapter((object(), object(), layout_obj),
                                         IHTML2LaTeXConverter)

    def test_component_is_registered(self):
        context = self.providing_stub([IRemark])
        request = self.providing_stub([IAddRemarkLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(type(view), RemarkLaTeXView)

    def test_component_implements_interface(self):
        self.assertTrue(ILaTeXView.implementedBy(RemarkLaTeXView))
        verifyClass(ILaTeXView, RemarkLaTeXView)


    def test_rendering(self):
        context = self.providing_stub([IRemark])
        self.expect(context.Title()).result('title')
        self.expect(context.getText()).result('foo <b>bar</b> baz')

        request = self.providing_stub([IAddRemarkLayer])

        layout = self.providing_stub([ILaTeXLayout])

        self.expect(layout.get_converter()).result(self.converter)
        self.expect(layout.use_package('color')).result(True)

        self.replay()

        view = queryMultiAdapter((context, request, layout),
                                 ILaTeXView)

        self.assertEquals(view.render(),
            '\\definecolor{light-gray}{gray}{0.8}\\fcolorbox{black}' + \
            '{light-gray}{\\parbox[r]{\\textwidth}{{\\bf title}\\\nfoo {' + \
            '\\bf bar} baz\n}}'
        )
