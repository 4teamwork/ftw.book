from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.interfaces import IPDFAssembler
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestBookInternalHyperlinksLaTeX(TestCase):
    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        self.book = create(Builder('book')
                           .titled('the book')
                           .with_layout(IDefaultBookLayoutSelectionLayer))

    def test_book_internal_hyperlinks_have_internal_reference(self):
        chapter = create(Builder('chapter')
                         .within(self.book)
                         .titled('the chapter'))

        html = 'Link to ' + \
            '<a class="internal-link"' + \
            ' href="resolveuid/%s">' % IUUID(chapter) + \
            'The Chapter</a>' + \
            '!'
        block = create(Builder('book textblock')
                       .within(chapter)
                       .having(text=html))

        request = block.REQUEST
        assembler = getMultiAdapter((self.book, request), IPDFAssembler)
        latex_view = getMultiAdapter((block, request, assembler.get_layout()),
                                     ILaTeXView)

        self.assertIn(
            r'\hyperref[path:/plone/the-book/the-chapter]{The Chapter'
            r'\footnote{See page'
            r' \pageref{path:/plone/the-book/the-chapter}}}',
            latex_view.render())
