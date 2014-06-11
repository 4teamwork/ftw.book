from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from unittest2 import TestCase
from zope.interface import noLongerProvides


class TestLatexInjectionExtender(TestCase):

    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        self.folder = create(Builder('folder'))
        self.page = create(Builder('page')
                           .titled('First page')
                           .within(self.folder))

    def add_book(self):
        self.book = create(Builder('book')
                           .titled('My Book')
                           .within(self.folder))

        self.chapter = create(Builder('chapter')
                              .titled('Chapter One')
                              .within(self.book))

        self.textblock = create(Builder('book textblock')
                                .titled('TextBlock One')
                                .within(self.chapter))

    def test_page_is_enabled_on_all_objects(self):
        self.add_book()
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
        self.add_book()
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
        self.add_book()
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

    def test_textblock_has_injected_fields(self):
        self.add_book()
        try:
            schema = self.textblock.Schema()

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
            noLongerProvides(self.textblock.REQUEST, IWithinBookLayer)

    def test_textblock_reordering(self):
        self.add_book()
        try:
            schema = self.textblock.Schema()
            fieldnames = schema.keys()

            # hideFromTOC should be right after showTitle
            self.assertEqual(fieldnames[fieldnames.index('showTitle') + 1],
                             'hideFromTOC')

        finally:
            # cleanup
            noLongerProvides(self.textblock.REQUEST, IWithinBookLayer)
