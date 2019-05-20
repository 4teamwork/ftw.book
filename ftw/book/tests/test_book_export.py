from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.book.tests.base import PDFDiffTestCase
import os
import unittest2


if not os.environ.get('SKIP_BOOK_EXPORTS', False):
    @unittest2.skip('PDF tests are currently flaky.')
    class TestPDFExport(PDFDiffTestCase):

        layer = BOOK_FUNCTIONAL_TESTING
        book_object_path = 'the-example-book'
        expected_result = 'books/test_book_export.pdf'
