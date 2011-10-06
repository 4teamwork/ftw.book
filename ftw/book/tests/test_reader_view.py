from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.view import ReaderView
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase
from mocker import ANY


class TestReaderView(MockTestCase):

    def test_get_book_obj(self):
        chapter = self.stub()
        book = self.providing_stub([IBook])
        self.set_parent(chapter, book)

        self.replay()

        view = ReaderView(chapter, object())

        self.assertEqual(view.get_book_obj(),
                         book)

    def test_get_book_obj_fails_when_there_is_no_book(self):
        context = self.set_parent(
            self.stub(),
            self.set_parent(
                self.stub(),
                self.providing_stub([IPloneSiteRoot])))

        self.replay()

        view = ReaderView(context, object())

        with self.assertRaises(Exception):
            view.get_book_obj()

    def test_get_toc_tree(self):
        book_brain = self.create_dummy(portal_type='Book')
        chapter_brain = self.create_dummy(portal_type='Chapter')
        paragraph_brain = self.create_dummy(showTitle=False,
                                            portal_type='Paragraph')

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

                        {'item': paragraph_brain,
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': True,
                         'currentItem': False,
                         'children': []}],

                 }],

            }

        view = ReaderView(object(), object())

        toc_tree = view.get_toc_tree(tree)

        expected_toc_tree = {
            'item': book_brain,
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': chapter_brain,
                 'depth': 1,
                 'currentParent': False,
                 'currentItem': False,
                 'children': [],
                 }]

            }

        self.assertEqual(toc_tree, expected_toc_tree)

        # The original tree should not be modified, so the paragraph
        # should be in the original tree dict.
        self.assertNotEqual(tree, toc_tree)
        self.assertEqual(len(tree.get('children')[0].get('children')), 1)
        self.assertEqual(len(toc_tree.get('children')[0].get('children')), 0)

        self.assertEqual(
            tree.get('children')[0].get('children')[0].get('item'),
            paragraph_brain)

    def test_render_toc(self):
        tree = {
            'item': {'getURL': '/book',
                     'Title': 'Book'},
            'depth': 0,
            'currentParent': False,
            'currentItem': True,
            'children': [

                {'item': {'getURL': '/book/chapt',
                          'Title': 'Chapter'},
                 'depth': 1,
                 'currentParent': False,
                 'currentItem': False,
                 'children': [

                        ]}

                ]}

        response = self.stub()
        self.expect(response.getHeader(ANY)).result('')
        self.expect(response.setHeader(ANY, ANY))

        request = self.stub()
        self.expect(request.debug).result(True)
        self.expect(request.response).result(response)

        self.replay()

        view = ReaderView(object(), request)
        html = view.render_toc(tree)

        self.assertIn('<a href="/book">Book</a>', html)
        self.assertIn('<a href="/book/chapt">Chapter</a>', html)
