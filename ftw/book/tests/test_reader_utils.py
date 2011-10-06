from unittest2 import TestCase
from ftw.book.browser.reader.utils import flaten_tree


class TestFlatenTree(TestCase):
    """Tests testing ftw.book.browser.reader.view.flaten_tree
    """

    def test_single_item(self):
        tree = {'item': 'A',
                'children': []}

        data = tuple(flaten_tree(tree))

        self.assertEqual(data, ('A',))

    def test_recursion(self):
        tree = {
            'item': 'A',
            'children': [

                {'item': 'B',
                 'children': [

                        {'item': 'C',
                         'children': []},

                        {'item': 'D',
                         'children': []}]},

                {'item': 'E',
                 'children': []}]}

        data = tuple(flaten_tree(tree))

        self.assertEqual(data, ('A', 'B', 'C', 'D', 'E'))
