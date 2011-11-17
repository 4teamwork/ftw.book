from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from mocker import ANY
from plone.mocktestcase import MockTestCase
from plonegov.pdflatex.browser.converter import LatexCTConverter
from zope.interface import directlyProvides


class TestLatexInjectionExtender(MockTestCase):

    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']

        self.folder = portal.get(portal.invokeFactory('Folder',
                                                      'latex-injection-test'))

        self.page = self.folder.get(
            self.folder.invokeFactory('Page', 'latex-test-page',
                                      title='First page'))

        self.book = self.folder.get(
            self.folder.invokeFactory('Book', 'latex-injection-book',
                                      title='My Book'))

        self.chapter = self.book.get(self.book.invokeFactory(
                'Chapter', 'chapter-one', title='Chapter One'))

    def tearDown(self):
        portal = self.layer['portal']
        portal.manage_delObjects(['latex-injection-test'])

    def test_page_is_enabled_on_all_objects(self):
        self.assertTrue(ILaTeXCodeInjectionEnabled.providedBy(self.folder))
        self.assertTrue(ILaTeXCodeInjectionEnabled.providedBy(self.page))
        self.assertTrue(ILaTeXCodeInjectionEnabled.providedBy(self.book))
        self.assertTrue(ILaTeXCodeInjectionEnabled.providedBy(self.chapter))

    def test_page_has_no_injected_fields(self):
        self.assertTrue(self.page.getField('preLatexCode') is None)
        self.assertTrue(self.page.getField('postLatexCode') is None)

    def test_folder_has_no_injected_fields(self):
        self.assertTrue(self.folder.getField('preLatexCode') is None)
        self.assertTrue(self.folder.getField('postLatexCode') is None)

    def test_book_has_injected_fields(self):
        self.assertTrue(self.book.getField('preLatexCode') is not None)
        self.assertTrue(self.book.getField('postLatexCode') is not None)

    def test_chapter_has_injected_fields(self):
        self.assertTrue(self.chapter.getField('preLatexCode') is not None)
        self.assertTrue(self.chapter.getField('postLatexCode') is not None)


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
