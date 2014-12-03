from Products.CMFCore.utils import getToolByName
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from unittest2 import TestCase
import transaction


def keywords_html(*keywords):
    return '\n'.join(
        map(lambda word: '<span class="keyword" title="%s">%s</span>' % (
            word, word), keywords))


def select2_javascripts():
    sources = [node.attrib.get('src') for node in browser.css('script')
               if node.attrib.get('src')]
    return filter(lambda src: 'select2' in src, sources)


class TestKeywordsView(TestCase):
    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.book = create(Builder('book').titled('The Book'))

    @browsing
    def test_keywords_only_available_when_use_keywords_enabled(self, browser):
        tab_label = 'Keywords'
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
    def test_keywords_are_ordered_normalized_case_insensitive(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .having(text=keywords_html('foo',
                                          'bar',
                                          'Baz',
                                          '\xc3\x84hnliches',
                                          '\xc3\xb6rtliches',
                                          '\xc3\x9cbliches')))

        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertEquals(
            ['',
             u'\xc4hnliches',
             'bar',
             'Baz',
             'foo',
             u'\xf6rtliches',
             u'\xdcbliches'],
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
    def test_message_when_there_are_no_results(self, browser):
        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals('No results found.',
                          browser.css('.no-results').first.text)

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
            'http://nohost/plone/the-book/the-chapter/' +
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

        self.assertEquals(['Bar,', 'Baz,', 'Foo'],
                          browser.css('.result-keywords span').text)

        self.assertEquals(['Foo'],
                          browser.css('.result-keywords b').text)

    @browsing
    def test_no_duplicate_keywords_in_result(self, browser):
        chapter = create(Builder('chapter').within(self.book))
        create(Builder('book textblock')
               .within(chapter)
               .titled('The Block')
               .having(text=keywords_html('Foo', 'Bar', 'Foo'),
                       showTitle=True))

        browser.login().open(self.book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['Bar,', 'Foo'],
                          browser.css('.result-keywords span').text)

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
             '/plone/the-book/first-chapter/first-subchapter/' +
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
            {'reader_url': 'http://nohost/plone/the-book/first-chapter/' +
             'first-subchapter/@@book_reader_view',
             'title': '1.1 First SubChapter',
             'position': 2},
            view.chapters['/plone/the-book/first-chapter/first-subchapter'])

    @browsing
    def test_only_search_for_results_in_this_book(self, browser):
        # Regression: when having the same keyword in multiple books
        # the keyword tab was broken because of unspecific query (no path).

        first_book = create(Builder('book').titled('First Book'))
        first_chapter = create(Builder('chapter').titled('First chapter')
                               .within(first_book))
        create(Builder('book textblock').titled('First Block')
               .within(first_chapter)
               .having(text=keywords_html('Foo', 'Bar')))

        second_book = create(Builder('book').titled('Second Book'))
        second_chapter = create(Builder('chapter').titled('Second chapter')
                                .within(second_book))
        create(Builder('book textblock').titled('Second Block')
               .within(second_chapter)
               .having(text=keywords_html('Bar', 'Baz')))

        browser.login().visit(first_book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'Bar', ''],
            browser.css('select[name=book_keywords] option').text,
            'Only keywords from the current book should be selectable.')

        browser.login().open(first_book,
                             {'book_keywords': 'Bar'},
                             view='tabbedview_view-keywords/load')
        self.assertEquals(1, len(browser.css('.result')),
                          'Only results from the current book should be'
                          ' found.')

    @browsing
    def test_select2_translations_are_loaded(self, browser):
        languages = getToolByName(self.layer['portal'], "portal_languages")

        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertEquals(
            ['++resource++ftw.book-select2/select2.js'],
            select2_javascripts(),
            'Expected no translation to be loaded for english.')

        languages.manage_setLanguageSettings('de', ['de'])
        transaction.commit()
        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertIn(
            '++resource++ftw.book-select2/select2_locale_de.js',
            select2_javascripts())

        languages.manage_setLanguageSettings('de-ch', ['de-ch'],
                                             setUseCombinedLanguageCodes=True)
        transaction.commit()
        browser.login().visit(self.book, view='tabbedview_view-keywords')
        self.assertIn(
            '++resource++ftw.book-select2/select2_locale_de.js',
            select2_javascripts())
