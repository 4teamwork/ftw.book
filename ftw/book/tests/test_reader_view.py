from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.browser.reader.view import ReaderView
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase
from json import loads
from mocker import ANY
from zope.component import provideAdapter
from zope.interface import Interface
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable


class TestReaderView(MockTestCase):

    def setUp(self):
        # Page templates use the traversing mechainsm for accessing
        # attributes on objects, so we need to register the default
        # traversable adapter.
        provideAdapter(factory=DefaultTraversable,
                       adapts=[Interface],
                       provides=ITraversable)

    def create_tree_from_brains(self, brains):
        tree = None
        brains.reverse()

        depth = 0

        for brain in brains:
            item = {'item': brain,
                    'depth': 0,
                    'children': tree and [tree] or []}
            tree = item
            depth += 1

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
                          u'data': [[u'1bookuid2', u'BOOK REPR']]})

    def test_render_next_with_uid(self):
        request = self.stub()
        self.expect(request.get('next_uid', '')).result('2chapter2')

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book1')

        chapter = self.stub()
        chapter_brain = self.stub()
        self.expect(chapter_brain.UID).result('2chapter2')
        self.expect(chapter_brain.getObject()).result(chapter)
        self.set_parent(chapter, book)

        paragraph = self.stub()
        paragraph_brain = self.stub()
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
                          u'data': [['2chapter2', 'CHAPTER REPR']]})

    def test_render_next_multi(self):
        request = self.stub()
        self.expect(request.get('next_uid', '')).result('two')

        renderer_factory = self.stub()
        self.mock_adapter(renderer_factory, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        brains = []
        for name in ('one', 'two', 'three', 'four', 'five'):
            obj = self.create_dummy()
            brain = self.stub()
            self.expect(brain.UID).result(name)
            self.expect(brain.getObject()).result(obj)
            brains.append(brain)

            renderer = self.stub()
            self.expect(renderer_factory(obj, ANY, ANY)).result(renderer)
            self.expect(renderer.render()).result(
                '%s content' % name)

        tree = self.create_tree_from_brains(brains)
        view = self.mocker.patch(ReaderView(object(), request))
        self.expect(view._tree).result(tree).count(1, None)

        self.replay()

        data = view.render_next(block_render_threshold=3)

        jsondata = loads(data)

        self.assertEqual(
            jsondata,
            {u'next_uid': u'five',
             u'data': [['two', 'two content'],
                       ['three', 'three content'],
                       ['four', 'four content']]})

    def test_render_previous(self):
        request = self.stub()
        self.expect(request.get('previous_uid', '')).result('2chapter2')

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book1')

        chapter = self.stub()
        chapter_brain = self.stub()
        self.expect(chapter_brain.UID).result('2chapter2')
        self.expect(chapter_brain.getObject()).result(chapter)
        self.set_parent(chapter, book)


        tree = self.create_tree_from_brains([
                book_brain, chapter_brain])

        view = self.mocker.patch(ReaderView(chapter, request))
        self.expect(view._tree).result(tree).count(1, None)

        chapter_renderer = self.mocker.mock()
        self.expect(chapter_renderer(ANY, ANY, ANY)).result(chapter_renderer)
        self.expect(chapter_renderer.render()).result('CHAPTER CONTENT')
        self.mock_adapter(chapter_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_previous(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(jsondata,
                         {u'previous_uid': u'1book1',
                          u'data': [['2chapter2', 'CHAPTER CONTENT']]})

    def test_render_previous_not_found(self):
        request = self.stub()
        self.expect(request.get('previous_uid', '')).result('any')

        book = self.providing_mock([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book')

        tree = self.create_tree_from_brains([book_brain])
        view = self.mocker.patch(ReaderView(book, request))
        self.expect(view._tree).result(tree).count(1, None)

        self.replay()

        self.assertEqual(view.render_previous(), u'{}')

    def test_render_previous_multi(self):
        request = self.stub()
        self.expect(request.get('previous_uid', '')).result('four')

        book = self.providing_mock([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book').count(1)

        brains = [book_brain]

        renderer_factory = self.stub()
        self.mock_adapter(renderer_factory, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        for name in ('one', 'two', 'three', 'four', 'five'):
            obj = self.create_dummy()
            brain = self.stub()
            self.expect(brain.UID).result(name)
            self.expect(brain.getObject()).result(obj)
            brains.append(brain)

            renderer = self.stub()
            self.expect(renderer_factory(obj, ANY, ANY)).result(renderer)
            self.expect(renderer.render()).result(
                '%s content' % name)

        tree = self.create_tree_from_brains(brains)
        view = self.mocker.patch(ReaderView(book, request))
        self.expect(view._tree).result(tree).count(1, None)

        self.replay()

        data = view.render_previous(block_render_threshold=3)
        jsondata = loads(data)

        self.assertEqual(
            jsondata,
            {u'previous_uid': u'one',
             u'data': [['two', 'two content'],
                       ['three', 'three content'],
                       ['four', 'four content']]})

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
        subchapter_brain = self.create_dummy(portal_type='Chapter')

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
                         'children': []},

                        {'item': subchapter_brain,
                         'currentParent': False,
                         'depth': 2,
                         '_pruneSubtree': False,
                         'currentItem': False,
                         'children': []}],

                 }],

            }

        view = ReaderView(object(), object())

        toc_tree = view.get_toc_tree(tree)

        expected_toc_tree = {
            'item': book_brain,
            'toc_number': None,
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

        # The original tree should not be modified, so the paragraph
        # should be in the original tree dict.
        self.assertNotEqual(tree, toc_tree)
        self.assertEqual(len(tree.get('children')[0].get('children')), 2)
        self.assertEqual(len(toc_tree.get('children')[0].get('children')), 1)

        self.assertEqual(
            tree.get('children')[0].get('children')[0].get('item'),
            paragraph_brain)

    def test_get_javascript_options_top(self):
        brains = []

        for uid in ('1book', '2chapter'):
            brains.append(self.create_dummy(UID=uid))

        context = self.stub()
        self.expect(context.UID()).result('1book')

        view = self.mocker.patch(ReaderView(context, object()))
        tree = self.create_tree_from_brains(brains)
        self.expect(view._tree).result(tree).count(0, None)

        self.replay()

        self.assertEqual(
            view.get_javascript_options(),
            {'prev_uid': None,
             'next_uid': '1book'})

    def test_get_javascript_options_not_top(self):
        brains = []

        for uid in ('1book', '2chapter'):
            brains.append(self.create_dummy(UID=uid))

        context = self.stub()
        self.expect(context.UID()).result('2chapter')

        view = self.mocker.patch(ReaderView(context, object()))
        tree = self.create_tree_from_brains(brains)
        self.expect(view._tree).result(tree).count(0, None)

        self.replay()

        self.assertEqual(
            view.get_javascript_options(),
            {'prev_uid': '1book',
             'next_uid': '2chapter'})

    def test_get_inline_javascript(self):

        view = self.mocker.patch(ReaderView(object(), object()))
        self.expect(view.get_javascript_options()).result({'foo': 'bar'})

        self.replay()

        self.assertEqual(
            view.get_inline_javascript(),
            'jq(function($) { init_reader_view({"foo": "bar"}); });')

    def test_get_navigation(self):
        brains = []

        for depth, title in enumerate(('Book', 'Chapter', 'SubChapter')):
            brains.append(self.create_dummy(
                    UID=title.lower(),
                    portal_type=depth == 0 and 'Book' or 'Chapter',
                    Title=title))

        context = self.stub()
        self.expect(context.UID()).result('book')

        request = self.stub()
        self.expect(request.debug).result(True)

        response = self.stub()
        self.expect(request.response).result(response)
        self.expect(response.getHeader('Content-Type')).result('text/html')

        view = self.mocker.patch(ReaderView(context, request))
        tree = self.create_tree_from_brains(brains)
        self.expect(view._tree).result(tree).count(0, None)

        self.replay()

        html = view.render_navigation()

        self.assertIn('<ul class="book-reader-navigation-0">', html)
        self.assertIn('<a href="#book">Book</a>', html)
        self.assertIn('<a href="#chapter">1 Chapter</a>', html)
        self.assertIn('<a href="#subchapter">1.1 SubChapter</a>', html)

