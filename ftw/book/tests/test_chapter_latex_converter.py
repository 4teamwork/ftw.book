from Acquisition import aq_inner, aq_parent
from mocker import ANY
from ftw.book.interfaces import IBook
from ftw.book.latex.chapter import ChapterLatexConverter
from plone.mocktestcase import MockTestCase
from zope.interface import directlyProvides


class TestChapterLatexConverter(MockTestCase):

    def test_converter(self):
        request = self.create_dummy()

        book = self.create_dummy()
        directlyProvides(book, IBook)

        context = self.mocker.mock()
        self.expect(aq_parent(aq_inner(context))).result(book)
        self.expect(context.pretty_title_or_id()).result('chapter title')

        view = self.mocker.mock()
        self.expect(view.level).result(1)
        self.expect(view.convert('chapter title')).result(
            'converted chapter title')
        self.expect(view.context).result(context)

        patch = self.mocker.patch(ChapterLatexConverter)
        self.expect(patch.convertChilds(ANY, ANY)).result(
            'child LaTeX')

        self.replay()

        latex = ChapterLatexConverter(context, request)(context, view)

        self.assertEqual(latex, '\n'.join((
                    r'\chapter{converted chapter title}',
                    'child LaTeX')))
