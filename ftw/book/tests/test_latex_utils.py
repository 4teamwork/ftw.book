from Acquisition import aq_inner, aq_parent
from ftw.book.interfaces import IBook
from ftw.book.latex.utils import getLatexHeading
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.mocktestcase import MockTestCase
from zope.interface import directlyProvides


class TestLatexHeading(MockTestCase):

    def test_latex_heading_of_primary_chapter(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')

        view = self.mocker.mock()
        self.expect(view.convert('My Chapter')).result('My Chapter')

        # view.level is 1 because we assume that we render the chapter
        # directly. If we'd render the parent of the chapter, view.level
        # but 2 when rendering the chapter.
        self.expect(view.level).result(1)
        self.expect(view.context).result(chapter)

        self.mocker.replay()

        self.assertEquals(getLatexHeading(chapter, view),
                          '\\chapter{My Chapter}\n')

    def test_latex_heading_of_primary_chapter_without_toc(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')

        view = self.mocker.mock()
        self.expect(view.convert('My Chapter')).result('My Chapter')

        # view.level is 1 because we assume that we render the chapter
        # directly. If we'd render the parent of the chapter, view.level
        # but 2 when rendering the chapter.
        self.expect(view.level).result(1)
        self.expect(view.context).result(chapter)


        self.mocker.replay()

        self.assertEquals(getLatexHeading(chapter, view, toc=False),
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

        view = self.mocker.mock()
        self.expect(view.convert('Sub chapter')).result('Sub chapter')

        # view.level is 1 because we assume that we render the chapter3
        # directly. If we'd render the parent of the chapter, view.level
        # but 2 when rendering the chapter3.
        self.expect(view.level).result(1)
        self.expect(view.context).result(chapter3)


        self.mocker.replay()

        self.assertEquals(getLatexHeading(chapter3, view),
                          '\\subsection{Sub chapter}\n')

    def test_heading_while_rendering_recursively(self):
        book = self.create_dummy()
        directlyProvides(book, IBook)

        # chapter1 = self.mocker.mock()

        chapter2 = self.mocker.mock()
        self.expect(chapter2.pretty_title_or_id()).result('Chapter two')

        view = self.mocker.mock()
        self.expect(view.convert('Chapter two')).result('Chapter two')

        # We assume that we run the PDF export recursively on the book, but
        # we are currently generating the heading of chapter2 - so we are
        # two levels deeper than when we'd run the export on chapter2
        # directly. The level is 1 + the differents.
        self.expect(view.level).result(3)
        self.expect(view.context).result(book)

        self.mocker.replay()

        self.assertEquals(getLatexHeading(chapter2, view),
                          '\\section{Chapter two}\n')

    def test_not_within_book(self):
        platform = self.create_dummy()
        directlyProvides(platform, INavigationRoot)

        chapter = self.mocker.mock()
        self.expect(aq_parent(aq_inner(chapter))).result(platform)
        self.expect(chapter.pretty_title_or_id()).result('Any chapter')

        view = self.mocker.mock()
        self.expect(view.convert('Any chapter')).result('Any chapter')

        self.expect(view.level).result(1)
        self.expect(view.context).result(chapter)

        self.mocker.replay()

        self.assertEquals(getLatexHeading(chapter, view),
                          '\\section{Any chapter}\n')
