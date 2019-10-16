from ftw.book.browser.reader.interfaces import IBookReaderRenderer
from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter


class TestBookRenderer(FunctionalTestCase):

    @browsing
    def test_title_is_rendered(self, browser):
        reader_view = self.example_book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((self.example_book, self.request, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())
        self.assertEquals('The Example Book', browser.css('h1').first.text)


class TestBlockRenderer(FunctionalTestCase):

    @browsing
    def test_is_rendered(self, browser):
        reader_view = self.example_book.empty.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((self.textblock, self.request, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())
        self.assertEquals('This is some text.', browser.css('p').first.text)

    @browsing
    def test_book_internal_links_are_marked_with_class(self, browser):
        chapter = self.example_book.introduction
        html = '<p><a class="internal-link"' + \
            ' href="resolveuid/%s">' % IUUID(chapter) + \
            'The Chapter</a></p>'
        self.textblock.text = RichTextValue(html)

        reader_view = self.example_book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter((self.textblock, self.request, reader_view),
                                   IBookReaderRenderer)
        browser.open_html(renderer.render())

        link = browser.find('The Chapter')
        self.assertIn('book-internal', link.classes)
        self.assertDictContainsSubset(
            {'data-uid': IUUID(chapter)},
            link.attrib)

    @browsing
    def test_links_to_itself_are_not_marked_as_book_internal(self, browser):
        # Some titles are linked to the default view of the context
        # so that we can exit the reader and edit things.
        # Theese links should not be changed to pointing to the reader view.
        # One example is the title of chapters.

        reader_view = self.example_book.restrictedTraverse('@@book_reader_view')
        renderer = getMultiAdapter(
            (self.example_book.empty, self.request, reader_view),
            IBookReaderRenderer)
        browser.open_html(renderer.render())

        link = browser.find('Empty')
        self.assertNotIn('book-internal', link.classes)
