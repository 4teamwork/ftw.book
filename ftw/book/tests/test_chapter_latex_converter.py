from Acquisition import aq_inner, aq_parent
from ftw.book.interfaces import IBook
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from simplelayout.types.common.interfaces import IPage
from zope.component import getMultiAdapter


class TestChapterLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_converter(self):
        request = self.create_dummy()
        book = self.providing_stub([IBook])

        chapter = self.providing_mock([IPage])
        self.expect(aq_parent(aq_inner(chapter))).result(book)
        self.expect(chapter.pretty_title_or_id()).result('chapter title')
        self.expect(chapter.listFolderContents()).result([])

        layout = self.mocker.mock()
        self.expect(layout.get_converter().convert('chapter title')).result(
            'converted chapter title')

        self.replay()

        view = getMultiAdapter((chapter, request, layout),
                               ILaTeXView)
        latex = view.render()

        self.assertEqual(latex, '\\chapter{converted chapter title}\n')
