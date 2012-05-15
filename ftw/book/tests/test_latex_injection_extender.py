from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from plone.mocktestcase import MockTestCase
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


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
        self.assertEquals(self.page.Schema().getField('preLatexCode'), None)
        self.assertEquals(self.page.Schema().getField('postLatexCode'), None)

    def test_folder_has_no_injected_fields(self):
        self.assertEquals(self.folder.Schema().getField('preLatexCode'), None)
        self.assertEquals(
            self.folder.Schema().getField('postLatexCode'), None)

    def test_book_has_injected_fields(self):
        # Usualy this happend during traversal - check layer.py
        # In this case a browser test could be the better way
        alsoProvides(self.book.REQUEST, IWithinBookLayer)

        self.assertNotEqual(self.book.Schema().getField('preLatexCode'), None)
        self.assertNotEqual(self.book.Schema().getField('postLatexCode'),
                            None)
        # cleanup
        noLongerProvides(self.book.REQUEST, IWithinBookLayer)

    def test_chapter_has_injected_fields(self):
        # Usualy this happend during traversal - check layer.py
        # In this case a browser test could be the better way
        alsoProvides(self.chapter.REQUEST, IWithinBookLayer)

        self.assertNotEqual(self.chapter.Schema().getField('preLatexCode'),
                            None)
        self.assertNotEqual(self.chapter.Schema().getField('postLatexCode'),
                            None)
        # cleanup
        noLongerProvides(self.chapter.REQUEST, IWithinBookLayer)
