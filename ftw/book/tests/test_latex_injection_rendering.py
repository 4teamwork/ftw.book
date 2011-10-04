from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from mocker import ANY
from plone.mocktestcase import MockTestCase
from plonegov.pdflatex.browser.converter import LatexCTConverter
from zope.interface import directlyProvides


class TestInjectionAwareConvertObject(MockTestCase):

    def test_not_injected_without_interface(self):
        view = object()

        obj = self.mocker.mock()
        self.expect(obj.getPhysicalPath()).result(['', 'myobj'])
        self.expect(obj.restrictedTraverse(
                '/myobj/pdflatex_convert_object')).result(None)

        self.expect(obj.getField(ANY)).count(0)

        self.replay()

        self.assertEqual(
            LatexCTConverter.convertObject(view, object=obj),
            '')

    def test_injected_with_interface(self):
        latex_pre_code = 'INJECTED PRE LATEX CODE'
        latex_post_code = 'INJECTED POST LATEX CODE'

        view = object()

        obj_dummy = self.create_dummy()

        directlyProvides(obj_dummy, ILaTeXCodeInjectionEnabled)
        obj = self.mocker.proxy(obj_dummy, spec=None)

        self.expect(obj.getField('preLatexCode').get(obj)).result(
            latex_pre_code)
        self.expect(obj.getField('postLatexCode').get(obj)).result(
            latex_post_code)

        self.expect(obj.getPhysicalPath()).result(
            ['', 'myobj']).count(0, None)
        self.expect(obj.restrictedTraverse(
                '/myobj/pdflatex_convert_object')).result(None)

        self.replay()
        latex = LatexCTConverter.convertObject(view, object=obj)

        self.assertIn(latex_pre_code, latex)
        self.assertIn(latex_post_code, latex)
        self.assertIn('/'.join(obj.getPhysicalPath()), latex)

    def test_injected_brain(self):
        latex_pre_code = 'INJECTED PRE LATEX CODE'
        latex_post_code = 'INJECTED POST LATEX CODE'

        obj_dummy = self.create_dummy()

        directlyProvides(obj_dummy, ILaTeXCodeInjectionEnabled)
        obj = self.mocker.proxy(obj_dummy, spec=None)

        self.expect(obj.getField('preLatexCode').get(obj)).result(
            latex_pre_code)
        self.expect(obj.getField('postLatexCode').get(obj)).result(
            latex_post_code)

        self.expect(obj.getPhysicalPath()).result(
            ['', 'myobj']).count(0, None)
        self.expect(obj.restrictedTraverse(
                '/myobj/pdflatex_convert_object')).result(None)
        self.expect(obj.restrictedTraverse('/myobj')).result(obj)

        brain = self.mocker.mock()
        self.expect(brain.getPath()).result('/myobj').count(2)

        view = self.mocker.mock()
        self.expect(view.context).result(obj).count(2)

        self.replay()
        latex = LatexCTConverter.convertObject(view, brain=brain)

        self.assertIn(latex_pre_code, latex)
        self.assertIn(latex_post_code, latex)
        self.assertIn('/'.join(obj.getPhysicalPath()), latex)
