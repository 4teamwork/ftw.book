from Acquisition import aq_inner, aq_parent
from StringIO import StringIO
from ftw.book.interfaces import IBook
from ftw.book.latex.utils import get_latex_heading
from ftw.book.latex.utils import get_raw_image_data
from ftw.testing import MockTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import directlyProvides


class TestLatexHeading(MockTestCase):

    def test_latex_heading_of_primary_chapter(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')

        layout = self.mocker.mock()
        self.expect(
            layout.get_converter().convert('My Chapter')).result(
            'My Chapter')

        self.mocker.replay()

        self.assertEquals(get_latex_heading(chapter, layout),
                          '\\chapter{My Chapter}\n')

    def test_latex_heading_of_primary_chapter_without_toc(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')

        layout = self.mocker.mock()
        self.expect(layout.get_converter().convert('My Chapter')
                    ).result('My Chapter')

        self.mocker.replay()

        self.assertEquals(get_latex_heading(chapter, layout, toc=False),
                          '\\chapter*{My Chapter}\n')

    def test_latex_heading_of_third_level_chapter(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        chapter1 = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter1))).result(book)

        chapter2 = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter2))).result(chapter1)

        chapter3 = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter3))).result(chapter2)
        self.expect(chapter3.pretty_title_or_id()).result('Sub chapter')

        layout = self.mocker.mock()
        self.expect(layout.get_converter().convert('Sub chapter')
                    ).result('Sub chapter')

        self.mocker.replay()

        self.assertEquals(get_latex_heading(chapter3, layout),
                          '\\subsection{Sub chapter}\n')

    def test_latex_heading_with_max_level_exceeded(self):
        book = self.providing_stub([IBook])

        # create 10 objects and use the last one
        obj = None
        previous = book
        for i in range(10):
            obj = self.mocker.mock()
            self.set_parent(obj, previous)
            previous = obj

        self.expect(obj.pretty_title_or_id()).result('the title')

        layout = self.mocker.mock()
        self.expect(layout.get_converter().convert('the title')
                    ).result('the title')

        self.mocker.replay()

        # subparagraph is the "smallest" heading..
        self.assertEquals(get_latex_heading(obj, layout),
                          '\\subparagraph{the title}\n')

    def test_not_within_book(self):
        platform = self.create_dummy()
        directlyProvides(platform, INavigationRoot)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(platform)
        self.expect(chapter.pretty_title_or_id()).result('Any chapter')

        layout = self.mocker.mock()
        self.expect(layout.get_converter().convert('Any chapter')
                    ).result('Any chapter')

        self.mocker.replay()

        self.assertEquals(get_latex_heading(chapter, layout),
                          '\\section{Any chapter}\n')

    def test_get_raw_image_data(self):
        already_raw = 'Image data'
        self.assertEquals(get_raw_image_data(already_raw),
                          already_raw)

        image = self.create_dummy(data=StringIO('stream data'))
        self.assertEquals(get_raw_image_data(image), 'stream data')

        image2 = self.create_dummy(data='direct data')
        self.assertEquals(get_raw_image_data(image2), 'direct data')
