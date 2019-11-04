from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.browser.reader.view import ReaderView
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase
from json import loads
from mocker import ANY
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import provideAdapter
from zope.interface import Interface
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable


class TestReaderView(MockTestCase):

    def setUp(self):
        super(TestReaderView, self).setUp()
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

    def test_call_would_render_tempalte(self):
        request = self.mocker.mock()
        self.expect(request.set('disable_border', True))
        self.expect(request.set('disable_plone.leftcolumn', True))
        self.expect(request.set('disable_plone.rightcolumn', True))
        view = self.mocker.patch(ReaderView(object(), request))
        self.expect(view.template()).result('TEMPLATE RESULT')

        self.replay()

        self.assertEqual(view(), 'TEMPLATE RESULT')

    def test_render_next_at_top(self):
        request = self.stub()
        self.expect(request.get('after_uid', '')).result('')
        self.expect(request.get('loaded_blocks[]', [])).result([])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.portal_type).result('Book')
        self.expect(book_brain.getObject()).result(book)
        self.expect(book.UID()).result('1bookuid2')
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

        self.assertEqual(
            jsondata,
            {u'insert_after': u'TOP',
             u'data': [[u'1bookuid2', u'BOOK REPR']],
             u'last_uid': u'1bookuid2',
             u'first_uid': u'1bookuid2'})

    def test_render_chapter_if_context_is_chapter(self):
        request = self.stub()
        self.expect(request.get('after_uid', '')).result('')
        self.expect(request.get('loaded_blocks[]', [])).result([])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.portal_type).result('Book')
        self.expect(book_brain.getObject()).result(book)
        self.expect(book_brain.UID).result('1book')

        chapter = self.set_parent(self.stub(), book)
        chapter_brain = self.stub()
        self.expect(chapter.UID()).result('2chapter')
        self.expect(chapter_brain.UID).result('2chapter')
        self.expect(chapter_brain.getObject()).result(chapter)

        view = self.mocker.patch(ReaderView(chapter, request))
        tree = self.create_tree_from_brains([book_brain, chapter_brain])
        self.expect(view._tree).result(tree).count(1, None)

        chapter_renderer = self.mocker.mock()
        self.expect(chapter_renderer(ANY, ANY, ANY)).result(chapter_renderer)
        self.expect(chapter_renderer.render()).result('CHAPTER REPR')
        self.mock_adapter(chapter_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_next(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(
            jsondata,
            {u'insert_after': u'TOP',
             u'data': [[u'2chapter', u'CHAPTER REPR']],
             u'last_uid': u'2chapter',
             u'first_uid': u'2chapter'})

    def test_render_next_with_uid(self):
        request = self.stub()
        self.expect(request.get('after_uid', '')).result('1book1')
        self.expect(request.get('loaded_blocks[]', [])).result(['1book1'])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book1')

        chapter = self.stub()
        chapter_brain = self.stub()
        self.expect(chapter_brain.UID).result('2chapter2')
        self.expect(chapter_brain.getObject()).result(chapter)
        self.set_parent(chapter, book)

        textblock = self.stub()
        textblock_brain = self.stub()
        self.expect(textblock_brain.UID).result('3textblock3')
        self.set_parent(textblock, chapter)

        tree = self.create_tree_from_brains([
                book_brain, chapter_brain, textblock_brain])

        view = self.mocker.patch(ReaderView(chapter, request))
        self.expect(view._tree).result(tree).count(1, None)

        textblock_renderer = self.mocker.mock()
        self.expect(textblock_renderer(ANY, ANY, ANY)).result(
            textblock_renderer)
        self.expect(textblock_renderer.render()).result('CHAPTER REPR')
        self.mock_adapter(textblock_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_next(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(
            jsondata,
            {u'insert_after': u'1book1',
             u'data': [[u'2chapter2', u'CHAPTER REPR']],
             u'last_uid': u'2chapter2',
             u'first_uid': u'2chapter2'})

    def test_render_next_multi(self):
        request = self.stub()
        self.expect(request.get('after_uid', '')).result('one')
        self.expect(request.get('loaded_blocks[]', [])).result(
            ['one', 'five'])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

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

        data = view.render_next()

        jsondata = loads(data)

        # "five" is not included since we already have loaded it.
        self.assertEqual(
            jsondata,
            {u'insert_after': u'one',
             u'data': [[u'two', u'two content'],
                       [u'three', u'three content'],
                       [u'four', u'four content']],
             u'last_uid': u'four',
             u'first_uid': u'two'})

    def test_render_previous(self):
        request = self.stub()
        self.expect(request.get('before_uid', '')).result('2chapter2')
        self.expect(request.get('loaded_blocks[]', [])).result(['2chapter2'])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_stub([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book1')
        self.expect(book_brain.getObject()).result(book)

        chapter = self.stub()
        chapter_brain = self.stub()
        self.expect(chapter_brain.UID).result('2chapter2')
        self.set_parent(chapter, book)

        tree = self.create_tree_from_brains([
                book_brain, chapter_brain])

        view = self.mocker.patch(ReaderView(chapter, request))
        self.expect(view._tree).result(tree).count(1, None)

        book_renderer = self.mocker.mock()
        self.expect(book_renderer(ANY, ANY, ANY)).result(book_renderer)
        self.expect(book_renderer.render()).result('BOOK CONTENT')
        self.mock_adapter(book_renderer, IBookReaderRenderer,
                          (Interface, Interface, Interface))

        self.replay()

        data = view.render_previous(block_render_threshold=1)
        jsondata = loads(data)

        self.assertEqual(jsondata,
                         {u'insert_before': u'2chapter2',
                          u'data': [[u'1book1', u'BOOK CONTENT']],
                          u'first_uid': u'1book1',
                          u'last_uid': u'1book1'})

    def test_render_previous_not_found(self):
        request = self.stub()
        self.expect(request.get('before_uid', '')).result('any')
        self.expect(request.get('loaded_blocks[]', [])).result(['any'])

        book = self.providing_mock([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book')

        tree = self.create_tree_from_brains([book_brain])
        view = self.mocker.patch(ReaderView(book, request))
        self.expect(view._tree).result(tree).count(1, None)

        self.replay()

        self.assertEqual(view.render_previous(), u'{}')

    def test_render_previous_requires_loaded_objects(self):
        # The content should be loaded first down (render_next), before
        # rendering up (render_previous).
        request = self.stub()
        self.expect(request.get('before_uid', '')).result('')
        self.expect(request.get('loaded_blocks[]', [])).result([])

        view = ReaderView(object(), request)

        self.replay()

        self.assertEqual(view.render_previous(), u'{}')

    def test_render_previous_multi(self):
        request = self.stub()
        self.expect(request.get('before_uid', '')).result('five')
        self.expect(request.get('loaded_blocks[]', [])).result(['five'])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_mock([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book')

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
            {u'insert_before': u'five',
             u'data': [[u'two', u'two content'],
                       [u'three', u'three content'],
                       [u'four', u'four content']],
             u'first_uid': u'two',
             u'last_uid': u'four'})

    def test_render_previous_multi_with_stop(self):
        request = self.stub()
        self.expect(request.get('before_uid', '')).result('five')
        self.expect(request.get('loaded_blocks[]', [])).result(
            ['five', 'two'])
        self.expect(request.response.setHeader('Content-Type',
                                               'application/json'))

        book = self.providing_mock([IBook])
        book_brain = self.stub()
        self.expect(book_brain.UID).result('1book')
        self.expect(book_brain.getObject()).result(book)

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

        data = view.render_previous(block_render_threshold=10)
        jsondata = loads(data)

        # "two" and "one" are not included, since "two" is already laoaded.
        self.assertEqual(
            jsondata,
            {u'insert_before': u'five',
             u'data': [[u'three', u'three content'],
                       [u'four', u'four content']],
             u'first_uid': u'three',
             u'last_uid': u'four'})

    def test_get_book_obj(self):
        chapter = self.stub()
        book = self.providing_stub([IBook])
        self.set_parent(chapter, book)

        self.replay()

        view = ReaderView(chapter, object())

        self.assertEqual(view.get_book_obj(),
                         book)
        self.assertEqual(view.book, book)

    def test_get_book_obj_fails_when_there_is_no_book(self):
        context = self.set_parent(
            self.stub(),
            self.set_parent(
                self.stub(),
                self.providing_stub([IPloneSiteRoot])))

        self.replay()

        view = ReaderView(context, object())

        with self.assertRaises(Exception) as cm:
            view.get_book_obj()

        exc = cm.exception
        self.assertEqual(str(exc), 'Could not find book.')

    def test_get_book_obj_fails_when_aq_top_is_reached(self):
        app = self.stub()
        self.expect(app.__parent__).result(None)
        context = self.stub()
        self.set_parent(context, app)

        self.replay()

        view = ReaderView(context, object())

        with self.assertRaises(Exception) as cm:
            view.get_book_obj()

        exc = cm.exception
        self.assertEqual(str(exc), 'Could not find book.')

    def test_render_block_does_not_fail_when_renderer_missing(self):
        brain = self.stub()
        obj = self.set_parent(self.stub(), None)
        self.expect(brain.getObject()).result(obj)

        context = self.stub()
        request = self.stub()

        self.replay()

        view = ReaderView(context, request)
        self.assertEqual(view.render_block(brain), '')

    def test_building_tree(self):
        catalog = self.mocker.mock()
        self.mock_tool(catalog, 'portal_catalog')
        self.expect(catalog.uniqueValuesFor('portal_type')).result(
            ('Book', 'Chapter', 'Page', 'Discussion Item', 'BookTextBlock'))

        book = self.stub()
        self.expect(book.getPhysicalPath()).result(['', 'site', 'book'])

        builder = self.mocker.replace(
            'plone.app.layout.navigation.navtree.buildFolderTree')
        self.expect(builder(book, obj=book, query={
                    'path': '/site/book',
                    # portal_type should not contain "Discussion Item"
                    'portal_type': ['Book', 'Chapter', 'Page',
                                    'BookTextBlock']
                    })).result({'tree': 1})

        self.replay()

        view = ReaderView(book, object())
        view._book = book

        self.expect(view.tree, {'tree': 1})

    def test_get_navigation(self):
        brains = []

        url = ''
        for depth, title in enumerate(('Book', 'Chapter', 'SubChapter')):
            url += '/%s' % title.lower()
            brains.append(self.create_dummy(
                UID=title.lower() + '-uid',
                portal_type=depth == 0 and 'Book' or 'Chapter',
                show_in_toc=True,
                Title=title,
                getURL=url))

        context = self.stub()
        self.expect(context.UID()).result('book-uid')
        self.expect(context.__parent__).result(None)

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
        self.assertIn('<a data-uid="book-uid" href="/book">Book</a>', html)

        self.assertIn(
            '<a data-uid="chapter-uid" href="/book/chapter">1 Chapter</a>',
            html)

        self.assertIn('<a data-uid="subchapter-uid"', html)
        self.assertIn('href="/book/chapter/subchapter">1.1 SubChapter</a>',
            html)
