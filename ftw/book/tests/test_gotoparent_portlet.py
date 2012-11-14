from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.interfaces import IBook
from ftw.book.portlets.gotoparent import Renderer
from ftw.testing import MockTestCase
from zope.component import provideAdapter
from zope.interface import Interface
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable


class TestPortletRenderer(MockTestCase):

    def setUp(self):
        super(TestPortletRenderer, self).setUp()
        # Page templates use the traversing mechainsm for accessing
        # attributes on objects, so we need to register the default
        # traversable adapter.
        provideAdapter(factory=DefaultTraversable,
                       adapts=[Interface],
                       provides=ITraversable)

        # create some objects with acquisition
        self.site = self.providing_stub([IPloneSiteRoot])

        self.folder = self.stub()
        self.set_parent(self.folder, self.site)
        self.expect(self.folder.Title()).result('The Folder')
        self.expect(self.folder.absolute_url()).result(
            'http://site/the-folder')

        self.book = self.providing_stub([IBook])
        self.set_parent(self.book, self.folder)

        self.chapter = self.stub()
        self.set_parent(self.chapter, self.book)

        self.block = self.stub()
        self.set_parent(self.block, self.chapter)

        # create request
        self.request = self.stub()
        self.expect(self.request.debug).result(True)

        response = self.stub()
        self.expect(response.getHeader('Content-Type')).result('text/html')
        self.expect(self.request.response).result(response)

    def test_get_book_not_in_book(self):
        self.replay()

        site_renderer = Renderer(self.site, None, None, None, None)
        self.assertEqual(site_renderer.get_book(), None)

        folder_renderer = Renderer(self.folder, None, None, None, None)
        self.assertEqual(folder_renderer.get_book(), None)

    def test_get_book_does_not_work_without_context(self):
        self.replay()

        context = None
        renderer = Renderer(context, None, None, None, None)

        self.assertEqual(renderer.get_book(), None)

    def test_get_book_works_on_book(self):
        self.replay()

        context = self.book
        renderer = Renderer(context, None, None, None, None)

        self.assertEqual(renderer.get_book(), self.book)

    def test_get_book_works_on_chapter(self):
        self.replay()

        context = self.chapter
        renderer = Renderer(context, None, None, None, None)

        self.assertEqual(renderer.get_book(), self.book)

    def test_get_book_works_on_block(self):
        self.replay()

        context = self.block
        renderer = Renderer(context, None, None, None, None)

        self.assertEqual(renderer.get_book(), self.book)

    def test_rendered_in_book(self):
        self.replay()

        renderer = Renderer(self.book, self.request, None, None, {})
        renderer.update()
        html = renderer.render()

        self.assertTrue(html.startswith(
                '<dl class="portlet portletGoToParent">'))

        self.assertIn(
            '<a href="http://site/the-folder">Return to '
            '<span>The Folder</span></a>',
            html)

    def test_not_rendered_outside_of_book(self):
        self.replay()

        context = self.folder
        renderer = Renderer(context, self.request, None, None, {})
        renderer.update()
        self.assertEquals(renderer.render(), '')
