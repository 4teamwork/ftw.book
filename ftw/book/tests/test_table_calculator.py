from ftw.book.table.calculator import ColumnWidthsCalculator
from unittest import TestCase


class TestTableCalculator(TestCase):

    def setUp(self):
        self.calculator = ColumnWidthsCalculator()

    def test_bad_entries(self):
        widths = [
            'james',
            'bond',
            '0-0-7',
        ]

        self.assertEquals(self.calculator(widths), [34, 33, 33])

    def test_number_as_string(self):
        widths = self.calculator(['20', '20', 0, 0, '-50'])
        self.assertEquals(widths, [20, 20, 5, 5, 50])

    def test_no_column(self):
        # One column
        self.assertEquals(self.calculator([]), [])

    def test_no_entries(self):
        # One column
        widths = self.calculator([0])
        self.assertEquals(widths, [100])
        # Two columns
        widths = self.calculator([0, 0])
        self.assertEquals(widths, [50, 50])

        # Tree columns
        widths = self.calculator([0, 0, 0])
        self.assertEquals(widths, [34, 33, 33])

    def test_minus_entries(self):
        widths = self.calculator([-50, 50])
        self.assertEquals(widths, [50, 50])

    def test_any_entries_less_than_100(self):
        widths = self.calculator([50, 0, 0, 0])
        self.assertEquals(widths, [52, 16, 16, 16])

    def test_all_entries_equals_100(self):
        widths = self.calculator([50, 20, 20, 10])
        self.assertEquals(widths, [50, 20, 20, 10])

    def test_any_entries_equals_100(self):
        widths = self.calculator([50, 50, 0, 0])
        self.assertEquals(widths, [25, 25, 25, 25])

    def test_any_entries_more_than_100(self):
        widths = self.calculator([50, 50, 1, 0])
        self.assertEquals(widths, [38, 37, 0, 25])

    def test_all_entries_less_than_100(self):
        widths = self.calculator([23, 44, 11])
        self.assertEquals(widths, [30, 56, 14])

    def test_all_entries_more_than_100(self):
        widths = self.calculator([30, 47, 24])
        self.assertEquals(widths, [31, 46, 23])
