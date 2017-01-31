from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.book.tests.base import PDFDiffTestCase
from unittest2 import skip
import os


if not os.environ.get('SKIP_BOOK_EXPORTS', False):
    @skip('XXX UPDATE ME')
    class TestPDFExport(PDFDiffTestCase):

        layer = BOOK_FUNCTIONAL_TESTING
        book_object_path = 'the-example-book'
        expected_result = 'books/test_book_export.pdf'
