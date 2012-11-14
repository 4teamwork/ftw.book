from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import ILaTeXInjectionController
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.interfaces import NO_PREFERRED_LAYOUT
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import directlyProvides
from zope.interface.verify import verifyClass


class TestInjectionAwareConvertObject(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestInjectionAwareConvertObject, self).setUp()

        context = self.create_dummy()
        request = self.providing_stub(IWithinBookLayer)
        builder = self.providing_stub(IBuilder)

        self.layout = BaseLayout(context, request, builder)

    def mock_extender_values(self, mock, **data):
        default_data = {'preLatexCode': '',
                        'postLatexCode': '',
                        'preferredColumnLayout': NO_PREFERRED_LAYOUT}
        default_data.update(data)
        data = default_data

        schema = self.stub()
        self.expect(mock.Schema()).result(schema).count(0, None)

        for fieldname, value in data.items():
            self.expect(schema.getField(fieldname).get(mock)).result(value)

        return schema

    def test_not_injected_without_interface(self):
        obj = self.mocker.mock()
        self.expect(obj.Schema()).count(0)

        self.replay()

        self.assertEqual(self.layout.render_latex_for(obj), '')

    def test_injected_with_interface(self):
        latex_pre_code = 'INJECTED PRE LATEX CODE'
        latex_post_code = 'INJECTED POST LATEX CODE'

        obj = self.providing_stub(ILaTeXCodeInjectionEnabled)

        self.mock_extender_values(obj, preLatexCode=latex_pre_code,
                                  postLatexCode=latex_post_code)

        self.expect(obj.getPhysicalPath()).result(
            ['', 'myobj']).count(3)  # 3 = pre + post + assertion below

        self.replay()
        latex = self.layout.render_latex_for(obj)

        self.assertIn(latex_pre_code, latex)
        self.assertIn(latex_post_code, latex)
        self.assertIn('/'.join(obj.getPhysicalPath()), latex)

    def test_bad_schemaextender_state(self):
        # sometimes the field can not be retrieved. We do nothing and we
        # don't fail in this case.
        obj_dummy = self.create_dummy()
        directlyProvides(obj_dummy, ILaTeXCodeInjectionEnabled)
        obj = self.mocker.proxy(obj_dummy, spec=None)
        self.mock_extender_values(obj, preLatexCode=None)

        self.replay()
        latex = self.layout.render_latex_for(obj)

        self.assertEqual(latex.strip(), '')

    def test_column_layout_injected(self):
        obj1 = self.providing_stub(ILaTeXCodeInjectionEnabled)
        self.mock_extender_values(
            obj1, preferredColumnLayout=NO_PREFERRED_LAYOUT)

        obj1a = self.providing_stub(ILaTeXCodeInjectionEnabled)
        self.mock_extender_values(
            obj1a, preferredColumnLayout=TWOCOLUMN_LAYOUT)

        obj1b = self.providing_stub(ILaTeXCodeInjectionEnabled)
        self.mock_extender_values(
            obj1b, preferredColumnLayout=ONECOLUMN_LAYOUT)

        obj1c = self.providing_stub(ILaTeXCodeInjectionEnabled)
        self.mock_extender_values(
            obj1c, preferredColumnLayout=NO_PREFERRED_LAYOUT)

        obj2 = self.providing_stub(ILaTeXCodeInjectionEnabled)
        self.mock_extender_values(
            obj2, preferredColumnLayout=TWOCOLUMN_LAYOUT)

        self.replay()

        latex_obj1 = self.layout.render_latex_for(obj1)
        latex_obj1a = self.layout.render_latex_for(obj1a)
        latex_obj1b = self.layout.render_latex_for(obj1b)
        latex_obj1c = self.layout.render_latex_for(obj1c)
        latex_obj2 = self.layout.render_latex_for(obj2)

        self.assertNotIn('column', latex_obj1)
        self.assertIn(r'\twocolumn', latex_obj1a)
        self.assertIn(r'\onecolumn', latex_obj1b)
        self.assertNotIn('column', latex_obj1c)
        self.assertIn(r'\twocolumn', latex_obj2)


class TestLaTeXInjectionController(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestLaTeXInjectionController, self).setUp()

        context = self.create_dummy()
        self.request = self.providing_stub(IWithinBookLayer)
        builder = self.create_dummy()

        self.layout = BaseLayout(context, self.request, builder)

    def test_component_is_registered(self):
        self.replay()
        component = queryMultiAdapter((self.layout, self.request),
                                      ILaTeXInjectionController)

        self.assertNotEquals(component, None)

    def test_component_implements_interface(self):
        self.replay()
        component = getMultiAdapter((self.layout, self.request),
                                    ILaTeXInjectionController)
        verifyClass(ILaTeXInjectionController, type(component))

    def test_columns_defaults_to_onecolumn(self):
        self.replay()
        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(),
                         ONECOLUMN_LAYOUT)

    def test_columns_layout_switching_is_persistent(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(), ONECOLUMN_LAYOUT)
        controller.set_layout(TWOCOLUMN_LAYOUT)
        self.assertEqual(controller.get_current_layout(), TWOCOLUMN_LAYOUT)

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(), TWOCOLUMN_LAYOUT)
        controller.set_layout(ONECOLUMN_LAYOUT)
        self.assertEqual(controller.get_current_layout(), ONECOLUMN_LAYOUT)

    def test_returns_latex_code(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)

        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')
        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT), '')

        self.assertEqual(controller.set_layout(TWOCOLUMN_LAYOUT),
                         r'\twocolumn')
        self.assertEqual(controller.set_layout(TWOCOLUMN_LAYOUT), '')
        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')

        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT),
                         r'\onecolumn')
        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT), '')
        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')
