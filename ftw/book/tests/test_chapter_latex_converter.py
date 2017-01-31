from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create


class TestChapterLaTeXView(FunctionalTestCase):

    def test_converter(self):
        self.assertEquals(
            '\\chapter{Empty}\n',
            self.get_latex_view_for(self.example_book.empty).render())

    def test_heading_counters_are_reset_when_export_context_is_book(self):
        """When only exporting a single chapter (or subchapter, ..),
        we need to increase the chapter counters on order to have the same
        number as if the whole book was exported.
        """

        book = self.example_book
        chapter = self.example_book.empty

        # The full book is exported => no need to change counters.
        self.assertEquals(
            '\\chapter{Empty}\n',
            self.get_latex_view_for(chapter, export_context=book).render())

        # Only the chapter is exported, so we need to set the chapter
        # counter to 2 in order to have number 3 for our chapter.
        self.assertEquals(
            '\\setcounter{chapter}{2}\n'
            '\\chapter{Empty}\n',
            self.get_latex_view_for(chapter, export_context=chapter).render())

        subchapter = create(Builder('chapter')
                            .titled(u'Subchapter').within(chapter))

        # The full book is exported => no need to change counters.
        self.assertEquals(
            '\\section{Subchapter}\n',
            self.get_latex_view_for(subchapter, export_context=book).render())

        # The parent chapter is exported, which includes our subchapter.
        # Because the parent context (=chapte) is exported, we should not change
        # any counters from the perspective of the subchapter, the parent chapter
        # renderer will take care of counters.
        self.assertEquals(
            '\\section{Subchapter}\n',
            self.get_latex_view_for(subchapter, export_context=chapter).render())

        # Only the subchapter is exported.
        # Since the subchapter number should be 3.1 we need to set the chapter
        # counter to 3 (because no parent chapter is rendered at all),
        # and the section counter to 0 so that we will end up with a 1 for the
        # next section.
        self.assertEquals(
            '\\setcounter{chapter}{3}\n'
            '\\setcounter{section}{0}\n'
            '\\section{Subchapter}\n',
            self.get_latex_view_for(subchapter, export_context=subchapter).render())
