from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.browser.reader.view import ReaderView
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase
from json import loads
from mocker import ANY
from zope.interface import Interface


class TestReaderView(MockTestCase):

    def create_tree_from_brains(self, brains):
        tree = None
        brains.reverse()

        for brain in brains:
            item = {'item': brain,
                    'children': tree and [tree] or []}
            tree = item

        return tree

    def test_render_next_at_top(self):
        request = self.stub()
        self.expect(request.get('next_uid', '')).result('')

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.portal_type).result('Book')
        self.expect(book_brain.getObject()).result(book)
        self.expect(book_brain.UID).result('1bookuid2')

        view = self.mocker.patch(ReaderView(book, request))

        tree = {'item': book_brain,
                'children': []}
        self.expect(view._tree).result(tree).count(1, None)

        book_renderer = self.mocker.mock()
        self.expect(book_renderer(ANY, ANY, ANY)).result(book_renderer)
        self.expect(book_renderer.render()).result('BOOK REPR')
        self.mock_adapter(book_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_next(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(jsondata,
                         {u'next_uid': None,
                          u'html': u'BOOK REPR'})

    def test_render_next_with_uid(self):
        request = self.stub()
        self.expect(request.get('next_uid', '')).result('2chapter2')

        book = self.providing_mock([IBook])
        book_brain = self.mocker.mock()
        self.expect(book_brain.UID).result('1book1')

        chapter = self.mocker.mock()
        chapter_brain = self.mocker.mock()
        self.expect(chapter_brain.UID).result('2chapter2')
        self.expect(chapter_brain.getObject()).result(chapter)
        self.set_parent(chapter, book)

        paragraph = self.mocker.mock()
        paragraph_brain = self.mocker.mock()
        self.expect(paragraph_brain.UID).result('3paragraph3')
        self.set_parent(paragraph, chapter)

        tree = self.create_tree_from_brains([
                book_brain, chapter_brain, paragraph_brain])

        view = self.mocker.patch(ReaderView(chapter, request))
        self.expect(view._tree).result(tree).count(1, None)

        paragraph_renderer = self.mocker.mock()
        self.expect(paragraph_renderer(ANY, ANY, ANY)).result(
            paragraph_renderer)
        self.expect(paragraph_renderer.render()).result('CHAPTER REPR')
        self.mock_adapter(paragraph_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_next(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(jsondata,
                         {u'next_uid': u'3paragraph3',
                          u'html': 'CHAPTER REPR'})

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
