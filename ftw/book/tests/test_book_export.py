from ftw.book.testing import EXAMPLE_CONTENT_INTEGRATION_TESTING
import unittest2
from ftw.book.tests.base import PDFDiffTestCase
import os


if not os.environ.get('SKIP_BOOK_EXPORTS', False):
    @unittest2.skip('PDF tests are currently flaky.')
    class TestPDFExport(PDFDiffTestCase):

        layer = EXAMPLE_CONTENT_INTEGRATION_TESTING
        book_object_path = 'example-book'
        expected_result = 'books/test_book_export.pdf'
