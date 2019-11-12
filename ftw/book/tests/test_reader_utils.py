from ftw.book.browser.utils import filter_tree
from ftw.book.browser.reader.utils import flaten_tree
from ftw.book.browser.utils import modify_tree
from unittest import TestCase


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


class TestFilterTree(TestCase):

    def test_filter_tree(self):
        tree = {
            'title': 'A',
            'remove': False,
            'children': [

                {'title': 'B',
                 'remove': True,
                 'children': []},

                {'title': 'C',
                 'remove': False,
                 'children': []},

                ]}

        expected_tree = {
            'title': 'A',
            'remove': False,
            'children': [

                {'title': 'C',
                 'remove': False,
                 'children': []}]}

        filtered_tree = filter_tree(lambda item: not item.get('remove'),
                                    tree)

        self.assertEqual(expected_tree, filtered_tree)
        self.assertNotEqual(filtered_tree, tree)

    def test_filter_tree_without_copy(self):
        tree = {
            'title': 'A',
            'remove': False,
            'children': [

                {'title': 'B',
                 'remove': True,
                 'children': []},

                {'title': 'C',
                 'remove': False,
                 'children': []},

                ]}

        expected_tree = {
            'title': 'A',
            'remove': False,
            'children': [

                {'title': 'C',
                 'remove': False,
                 'children': []}]}

        filtered_tree = filter_tree(lambda item: not item.get('remove'),
                                    tree,
                                    copy=False)

        self.assertEqual(expected_tree, filtered_tree)
        self.assertEqual(filtered_tree, tree)

    def test_filter_tree_filter_root(self):
        tree = {
            'title': 'A',
            'remove': True,
            'children': [

                {'title': 'B',
                 'remove': False,
                 'children': []}
                ]
            }

        expected_tree = None

        self.assertEqual(filter_tree(lambda item: not item.get('remove'),
                                     tree),
                         expected_tree)

    def test_object_not_copied(self):
        myobj = object()

        tree = {
            'item': myobj,
            'children': []}

        filtered_tree = filter_tree(lambda item: True, tree, copy=True)

        # Only structure (dicts, lists) should be copied, but the values
        # of the dicts.
        self.assertEqual(tree.get('item'), filtered_tree.get('item'))


class TestModifyTree(TestCase):

    def test_modification(self):
        tree = {
            'title': 'one',
            'children': [

                {'title': 'two',
                 'children': []}]}

        expected_tree = {
            'title': 'one',
            'foo': 'Title one',
            'parent': None,
            'children': [

                {'title': 'two',
                 'foo': 'Title two',
                 'parent': 'Title one',
                 'children': []}]}

        def modifier(node, parent):
            node['foo'] = 'Title %s' % node.get('title')
            node['parent'] = parent and parent.get('foo')

        result_tree = modify_tree(modifier, tree)

        self.assertEqual(result_tree, expected_tree)
