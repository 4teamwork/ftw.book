from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.book.tests.base import PDFDiffTestCase


class TestPDFExport(PDFDiffTestCase):
    layer = BOOK_FUNCTIONAL_TESTING
    expected_result = 'books/test_book_export.pdf'
