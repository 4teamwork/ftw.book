from ftw.book.browser.toc_tree import BookTocTree
from ftw.testing import MockTestCase


class TestTocTree(MockTestCase):

    def test_get_toc_tree(self):
        book_brain = self.create_dummy(portal_type='Book',
                                       show_in_toc=True)
        chapter_brain = self.create_dummy(portal_type='Chapter',
                                          show_in_toc=True)
        textblock_brain = self.create_dummy(show_in_toc=False,
                                            portal_type='BookTextBlock')
        textblock2_brain = self.create_dummy(show_in_toc=False,
                                             portal_type='BookTextBlock')
        subchapter_brain = self.create_dummy(portal_type='Chapter',
                                             show_in_toc=True)

        tree = {
            'item': book_brain,
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': chapter_brain,
                 'depth': 1,
                 'currentParent': False,
                 'currentItem': False,
                 'children': [

                        {'item': textblock_brain,
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': True,
                         'currentItem': False,
                         'children': []},

                        {'item': textblock2_brain,
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': True,
                         'currentItem': False,
                         'children': []},

                        {'item': subchapter_brain,
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': False,
                         'currentItem': False,
                         'children': []}],

                 }],

            }


        toc_tree_gen = BookTocTree()
        toc_tree = toc_tree_gen(tree)

        expected_toc_tree = {
            'item': book_brain,
            'toc_number': '',
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': chapter_brain,
                 'toc_number': '1',
                 'depth': 1,
                 'currentParent': False,
                 'currentItem': False,
                 'children': [

                        {'item': subchapter_brain,
                         'toc_number': '1.1',
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': False,
                         'currentItem': False,
                         'children': []}],
                 }]

            }

        self.assertEqual(toc_tree, expected_toc_tree)
        # The original tree should not be modified, so the textblock
        # should be in the original tree dict.
        self.assertNotEqual(tree, toc_tree)
        self.assertEqual(len(tree.get('children')[0].get('children')), 3)
        self.assertEqual(len(toc_tree.get('children')[0].get('children')), 1)

        self.assertEqual(
            tree.get('children')[0].get('children')[0].get('item'),
        textblock_brain)
