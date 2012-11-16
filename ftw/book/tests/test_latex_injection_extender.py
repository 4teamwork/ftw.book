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

        self.folder = portal.get(portal.invokeFactory(
                'Folder',
                'latex-injection-test'))

        self.page = self.folder.get(
            self.folder.invokeFactory('Page', 'latex-test-page',
                                      title='First page'))

        self.book = self.folder.get(
            self.folder.invokeFactory('Book', 'latex-injection-book',
                                      title='My Book'))

        self.chapter = self.book.get(self.book.invokeFactory(
                'Chapter', 'chapter-one', title='Chapter One'))

        self.paragraph = self.chapter.get(self.chapter.invokeFactory(
                'Paragraph', 'paragraph-one', title='Paragraph One'))

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
        self.assertEquals(self.folder.Schema().getField('preLatexCode'),
                          None)
        self.assertEquals(
            self.folder.Schema().getField('postLatexCode'), None)

    def test_book_has_injected_fields(self):
        # Usualy this happend during traversal - check layer.py
        # In this case a browser test could be the better way
        alsoProvides(self.book.REQUEST, IWithinBookLayer)

        try:
            schema = self.book.Schema()

            # general book fields
            self.assertTrue(schema.getField('preLatexCode'))
            self.assertTrue(schema.getField('postLatexCode'))
            self.assertTrue(schema.getField('preferredColumnLayout'))
            self.assertFalse(schema.getField('latexLandscape'))
            self.assertFalse(schema.getField('preLatexClearpage'))
            self.assertFalse(schema.getField('postLatexClearpage'))
            self.assertFalse(schema.getField('preLatexNewpage'))
            self.assertFalse(schema.getField('hideFromTOC'))

        finally:
            # cleanup
            noLongerProvides(self.book.REQUEST, IWithinBookLayer)

    def test_chapter_has_injected_fields(self):
        # Usualy this happend during traversal - check layer.py
        # In this case a browser test could be the better way
        alsoProvides(self.chapter.REQUEST, IWithinBookLayer)

        try:
            schema = self.chapter.Schema()

            # general book fields
            self.assertTrue(schema.getField('preLatexCode'))
            self.assertTrue(schema.getField('postLatexCode'))
            self.assertTrue(schema.getField('preferredColumnLayout'))
            self.assertTrue(schema.getField('latexLandscape'))
            self.assertTrue(schema.getField('preLatexClearpage'))
            self.assertTrue(schema.getField('postLatexClearpage'))
            self.assertTrue(schema.getField('preLatexNewpage'))
            self.assertFalse(schema.getField('hideFromTOC'))

        finally:
            # cleanup
            noLongerProvides(self.chapter.REQUEST, IWithinBookLayer)

    def test_paragraph_has_injected_fields(self):
        # Usualy this happend during traversal - check layer.py
        # In this case a browser test could be the better way
        alsoProvides(self.paragraph.REQUEST, IWithinBookLayer)

        try:
            schema = self.paragraph.Schema()

            # general book fields
            self.assertTrue(schema.getField('preLatexCode'))
            self.assertTrue(schema.getField('postLatexCode'))
            self.assertTrue(schema.getField('preferredColumnLayout'))
            self.assertTrue(schema.getField('latexLandscape'))
            self.assertTrue(schema.getField('preLatexClearpage'))
            self.assertTrue(schema.getField('postLatexClearpage'))
            self.assertTrue(schema.getField('preLatexNewpage'))
            self.assertTrue(schema.getField('hideFromTOC'))

        finally:
            # cleanup
            noLongerProvides(self.paragraph.REQUEST, IWithinBookLayer)

    def test_paragraph_reordering(self):
        alsoProvides(self.paragraph.REQUEST, IWithinBookLayer)

        try:
            schema = self.paragraph.Schema()
            fieldnames = schema.keys()

            # hideFromTOC should be right after showTitle
            self.assertEqual(fieldnames[fieldnames.index('showTitle') + 1],
                             'hideFromTOC')

        finally:
            # cleanup
            noLongerProvides(self.paragraph.REQUEST, IWithinBookLayer)
