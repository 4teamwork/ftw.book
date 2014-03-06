from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase
import transaction


def keywords_html(*keywords):
    return '\n'.join(
        map(lambda word: '<span class="keyword" title="%s">%s</span>' % (
                word, word), keywords))


class TestKeywordsView(TestCase):
    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book').titled('The Book'))

    @browsing
    def test_keywords_only_available_when_use_keywords_enabled(self, browser):
        tab_label = 'keywords'  # needs to be translated to english
        browser.login().visit(self.book, view='tabbed_view')
        self.assertNotIn(tab_label, browser.css('.tabbedview-tabs a').text)

        self.book.setUse_index(True)
        transaction.commit()

        browser.login().visit(self.book, view='tabbed_view')
        self.assertIn(tab_label, browser.css('.tabbedview-tabs a').text)

    @browsing
    def test_keywords_tab_is_available(self, browser):
        browser.login().visit(self.book, view='tabbedview_view-keywords')

    @browsing
    def test_keywords_tab_provides_select_with_keywords(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('Foo', 'bar', 'Baz')))

        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'bar', 'Baz', ''],
            browser.css('select[name=book_keywords] option').text)

    @browsing
    def test_no_duplicate_keywords(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('Foo', 'bar', 'Foo')))

        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'bar', ''],
            browser.css('select[name=book_keywords] option').text)

    @browsing
    def test_keywords_are_ordered_case_insensitive(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('foo', 'bar', 'Baz')))

        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertEquals(
            ['', 'bar', 'Baz', 'foo'],
            browser.css('select[name=book_keywords] option').text)

    @browsing
    def test_load_results_by_keyword(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('Foo')))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('Bar')))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')
        self.assertEquals(1, len(browser.css('.result')),
                          'Expected exactly one result')

    @browsing
    def test_results_are_sorted_by_position_in_the_book(self, browser):
        one = create(Builder('chapter')
                     .titled('Chapter One')
                     .within(self.book))

        two = create(Builder('chapter')
                     .titled('Chapter Two')
                     .within(self.book))

        # Create blocks in reversed order for verifying that they are
        # actually sorted correctly.

        create(Builder('book textblock')
               .within(two)
               .titled('Block 2.2')
               .having(text=keywords_html('Foo'),
                       showTitle=True))

        block = create(Builder('book textblock')
                       .within(two)
                       .titled('Block 2.1')
                       .having(text=keywords_html('Foo'),
                               showTitle=True))
        two.moveObjectsByDelta([block.getId()], -1)

        create(Builder('book textblock')
               .within(one)
               .having(text=keywords_html('Foo')))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['1 Chapter One',
                           '2.1 Block 2.1',
                           '2.2 Block 2.2'],
                          browser.css('.result .title').text)

    @browsing
    def test_block_title_is_shown(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .titled('The Block')
               .having(text=keywords_html('Foo'),
                       showTitle=True))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals('1.1 The Block',
                          browser.css('.result .title').first.text)

    @browsing
    def test_chapter_title_used_when_block_title_invisible(self, browser):
        chapter = create(Builder('chapter')
                         .within(self.book)
                         .titled('The Chapter'))
        create(Builder('book textblock')
               .within(chapter)
               .titled('The Block')
               .having(text=keywords_html('Foo'),
                       showTitle=False))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals('1 The Chapter',
                          browser.css('.result .title').first.text)

    @browsing
    def test_title_is_linked_with_reader(self, browser):
        chapter = create(Builder('chapter')
                         .titled('The Chapter')
                         .within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .titled('The Block')
               .having(text=keywords_html('Foo'),
                       showTitle=True))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(
            'http://nohost/plone/the-book/the-chapter/' + \
                'the-block/@@book_reader_view',
            browser.find('1.1 The Block').attrib['href'])

    @browsing
    def test_keywords_are_shown_foreach_result(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .titled('The Block')
               .having(text=keywords_html('Foo', 'Bar', 'Baz'),
                       showTitle=True))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['Foo,', 'Bar,', 'Baz'],
                          browser.css('.result-keywords span').text)

        self.assertEquals(['Foo'],
                          browser.css('.result-keywords b').text)

    @browsing
    def test_result_location_is_shown(self, browser):
        chapter = create(Builder('chapter')
                         .titled('Chapter')
                         .within(self.book))

        subchapter = create(Builder('chapter')
                            .titled('SubChapter')
                            .within(chapter))

        create(Builder('book textblock')
               .within(subchapter)
               .titled('The Block')
               .having(text=keywords_html('Foo'),
                       showTitle=True))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['The Book', '1 Chapter', '1.1 SubChapter'],
                          browser.css('.result-location a').text)

        self.assertEquals(
            'http://nohost/plone/the-book/@@book_reader_view',
            browser.css('.result-location a').first.attrib['href'])

    def test_chapters_cache(self):
        first = create(Builder('chapter')
                       .titled('First Chapter')
                       .within(self.book))
        first_sub = create(Builder('chapter')
                           .titled('First SubChapter')
                           .within(first))
        create(Builder('chapter')
               .titled('First SubSubChapter')
               .within(first_sub))
        create(Builder('chapter')
               .titled('Second Chapter')
               .within(self.book))

        view = self.book.restrictedTraverse('tabbedview_view-keywords')

        self.assertItemsEqual(
            ['/plone/the-book',
             '/plone/the-book/first-chapter',
             '/plone/the-book/first-chapter/first-subchapter',
             '/plone/the-book/first-chapter/first-subchapter/' + \
                 'first-subsubchapter',
             '/plone/the-book/second-chapter'],
            view.chapters.keys())

        self.assertDictContainsSubset(
            {'reader_url': 'http://nohost/plone/the-book/@@book_reader_view',
             'title': 'The Book',
             'position': 0},
            view.chapters['/plone/the-book'])
        self.assertIn('brain', view.chapters['/plone/the-book'])

        self.assertDictContainsSubset(
            {'reader_url': 'http://nohost/plone/the-book/first-chapter/' + \
                 'first-subchapter/@@book_reader_view',
             'title': '1.1 First SubChapter',
             'position': 2},
            view.chapters['/plone/the-book/first-chapter/first-subchapter'])
