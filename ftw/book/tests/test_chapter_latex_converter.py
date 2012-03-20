from Acquisition import aq_inner, aq_parent
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IChapter
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter


class TestChapterLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_converter(self):
        request = self.create_dummy()
        book = self.providing_stub([IBook])

        chapter = self.providing_mock([IChapter])
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('chapter title')
        self.expect(chapter.listFolderContents()).result([])

        layout = self.mocker.mock()
        self.expect(layout.context).result(book).count(2)
        self.expect(layout.get_converter().convert('chapter title')).result(
            'converted chapter title')

        self.replay()

        view = getMultiAdapter((chapter, request, layout),
                               ILaTeXView)
        latex = view.render()

        self.assertEqual(latex, '\\chapter{converted chapter title}\n')

    def test_get_heading_counters_latex_with_book(self):
        request = self.create_dummy()
        book = self.providing_stub([IBook])
        chapter = self.providing_stub([IChapter])
        self.set_parent(chapter, book)

        layout = self.stub()
        self.expect(layout.context).result(book)

        self.replay()

        view = getMultiAdapter((chapter, request, layout), ILaTeXView)

        # Since we are exporting the book and not the chapter directly
        # there is no need to reset the heading counters.
        self.assertEqual(view.get_heading_counters_latex(), '')

    def test_get_heading_counters_latex_with_chapter(self):
        request = self.create_dummy()

        book = self.providing_stub([IBook])
        chapter1 = self.providing_stub([IChapter])
        chapter2 = self.providing_stub([IChapter])
        chapter2a = self.providing_stub([IChapter])
        chapter2b = self.providing_stub([IChapter])

        self.expect(chapter1.portal_type).result('Chapter')
        self.expect(chapter2.portal_type).result('Chapter')
        self.expect(chapter2a.portal_type).result('Chapter')
        self.expect(chapter2b.portal_type).result('Chapter')

        self.expect(book.contentValues()).result([chapter1, chapter2])
        self.set_parent(chapter1, book)
        self.set_parent(chapter2, book)

        self.expect(chapter2.contentValues()).result(
            [chapter2a, chapter2b])
        self.set_parent(chapter2a, chapter2)
        self.set_parent(chapter2b, chapter2)

        self.expect(chapter1.contentValues()).result([])
        self.expect(chapter2a.contentValues()).result([])
        self.expect(chapter2b.contentValues()).result([])

        self.replay()

        # We are exporting the chapter directly, so there is no book / parent
        # chapter heading and we need to reset the heading counters.

        layout2a = self.create_dummy(context=chapter2a)
        view2a = getMultiAdapter((chapter2a, request, layout2a), ILaTeXView)
        self.assertEqual(view2a.get_heading_counters_latex(), '\n'.join((
                    r'\setcounter{chapter}{2}',
                    r''
                    )))

        layout2b = self.create_dummy(context=chapter2b)
        view2b = getMultiAdapter((chapter2b, request, layout2b), ILaTeXView)
        self.assertEqual(view2b.get_heading_counters_latex(), '\n'.join((
                    r'\setcounter{chapter}{2}',
                    r'\setcounter{section}{1}',
                    r''
                    )))
