from Products.CMFCore.utils import getToolByName
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.book.testing import EXAMPLE_CONTENT_INTEGRATION_TESTING
from ftw.book.tests import export
from ftw.pdfgenerator.utils import provide_request_layer
from plone.browserlayer.layer import mark_layer
from plone.mocktestcase.dummy import Dummy
from unittest2 import TestCase
import os


DIRNAME = 'test_book_export'


class TestPDFExport(TestCase):

    layer = EXAMPLE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        assert os.getcwd().endswith('/parts/test'), \
            'Assumed the working directory is .../parts/test, ' \
            'but it is %s' % os.getcwd()

        if DIRNAME in os.listdir('.'):
            os.system('rm -r %s' % DIRNAME)
        os.mkdir(DIRNAME)
        self.resultdir = os.path.abspath(DIRNAME)

        from ftw.book import tests
        self.booksdir = os.path.join(os.path.dirname(tests.__file__), 'books')

        self.book = self.layer['portal'].get('example-book')

        mark_layer(None, Dummy(request=self.book.REQUEST))
        provide_request_layer(self.book.REQUEST, IWithinBookLayer)
        provide_request_layer(self.book.REQUEST,
                              IDefaultBookLayoutSelectionLayer)

        # configure langueg to german, since the test book is german
        tool = getToolByName(self.layer['portal'], "portal_languages")
        tool.manage_setLanguageSettings('de', ['de'])

    def test_book_export(self):
        filenamebase = 'test_book_export'

        target = os.path.join(self.resultdir, '%s.pdf' % filenamebase)
        export.export_pdf(self.book, target)

        expectation = os.path.join(self.booksdir, '%s.pdf' % filenamebase)
        difference = os.path.join(self.resultdir,
                                  '%s-diff.pdf' % filenamebase)
        failed_pages = export.diff_pdfs(target, expectation, difference)

        self.assertEqual(
            len(failed_pages), 0,

            '\n'.join((
                    'The built PDF does not match the expected PDF.',
                    'Differing page(s): %s' % ', '.join(
                        map(str, failed_pages)),
                    'Result PDF:        %s' % target,
                    'Expected PDF:      %s' % expectation,
                    'Diff PDF:          %s' % difference)))
