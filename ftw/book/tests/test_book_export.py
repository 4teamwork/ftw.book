from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.book.tests.base import PDFDiffTestCase
import os


if not os.environ.get('SKIP_BOOK_EXPORTS', False):
    class TestPDFExport(PDFDiffTestCase):

        layer = BOOK_FUNCTIONAL_TESTING
        book_object_path = 'example-book'
        expected_result = 'books/test_book_export.pdf'
        profiles = ['ftw.book.tests:examplecontent']
