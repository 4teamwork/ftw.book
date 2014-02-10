from ftw.book.testing import EXAMPLE_CONTENT_INTEGRATION_TESTING
from ftw.book.tests.base import PDFDiffTestCase
import os


if not os.environ.get('SKIP_BOOK_EXPORTS', False):
    class TestPDFExport(PDFDiffTestCase):

        layer = EXAMPLE_CONTENT_INTEGRATION_TESTING
        book_object_path = 'example-book'
        expected_result = 'books/test_book_export.pdf'
