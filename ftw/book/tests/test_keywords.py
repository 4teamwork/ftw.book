from Products.CMFCore.utils import getToolByName
from ftw.book.testing import LanguageSetter
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
import transaction


def keywords_html(*keywords):
    return RichTextValue('<p>{}</p>'.format('\n'.join(
        map(lambda word: '<span class="keyword" title="%s">%s</span>' % (
            word, word), keywords))))


def select2_javascripts():
    sources = [node.attrib.get('src') for node in browser.css('script')
               if node.attrib.get('src')]
    return filter(lambda src: 'select2' in src, sources)


class TestKeywordsView(FunctionalTestCase, LanguageSetter):

    @browsing
    def test_keywords_only_available_when_use_keywords_enabled(self, browser):
        tab_label = 'Keywords'
        browser.login().visit(self.example_book, view='tabbed_view')
        self.assertNotIn(tab_label, browser.css('.tabbedview-tabs a').text)

        self.example_book.use_index = True
        transaction.commit()

        browser.login().visit(self.example_book, view='tabbed_view')
        self.assertIn(tab_label, browser.css('.tabbedview-tabs a').text)

    @browsing
    def test_keywords_tab_is_available(self, browser):
        browser.login().visit(self.example_book,
                              view='tabbedview_view-keywords')

    @browsing
    def test_keywords_tab_provides_select_with_keywords(self, browser):
        self.grant('Manager')
        self.textblock.text = keywords_html('Foo', 'bar', 'Baz')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'bar', 'Baz', ''],
            browser.css('select[name=book_keywords] option').text)

    @browsing
    def test_no_duplicate_keywords(self, browser):
        self.grant('Manager')
        self.textblock.text = keywords_html('Foo', 'bar', 'Foo')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'bar', ''],
            browser.css('select[name=book_keywords] option').text)

    @browsing
    def test_keywords_are_ordered_normalized_case_insensitive(self, browser):
        self.textblock.text = keywords_html('foo',
                                            'bar',
                                            'Baz',
                                            '\xc3\x84hnliches',
                                            '\xc3\xb6rtliches',
                                            '\xc3\x9cbliches')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
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
        self.textblock.text = keywords_html('Foo')
        self.textblock.reindexObject()
        self.textblock2.text = keywords_html('Bar')
        self.textblock2.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')
        self.assertEquals(1, len(browser.css('.result')),
                          'Expected exactly one result')

    @browsing
    def test_message_when_there_are_no_results(self, browser):
        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals('No results found.',
                          browser.css('.no-results').first.text)

    @browsing
    def test_results_are_sorted_by_position_in_the_book(self, browser):
        one = create(Builder('chapter')
                     .titled('Chapter One')
                     .within(self.example_book))

        two = create(Builder('chapter')
                     .titled('Chapter Two')
                     .within(self.example_book))

        # Create blocks in reversed order for verifying that they are
        # actually sorted correctly.

        create(Builder('book textblock')
               .within(two)
               .titled('Block 2.2')
               .having(text=keywords_html('Foo'),
                       show_title=True))

        block = create(Builder('book textblock')
                       .within(two)
                       .titled('Block 2.1')
                       .having(text=keywords_html('Foo'),
                               show_title=True))
        two.moveObjectsByDelta([block.getId()], -1)

        create(Builder('book textblock')
               .within(one)
               .having(text=keywords_html('Foo'),
                       show_title=False))

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['4 Chapter One',
                           '5.1 Block 2.1',
                           '5.2 Block 2.2'],
                          browser.css('.result .title').text)

    @browsing
    def test_block_title_is_shown_when_activated(self, browser):
        self.textblock.text = keywords_html('Foo')
        self.textblock.show_title = False
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        # show_title is False => show chapter title
        self.assertEquals(['2.1 China'],
                          browser.css('.result .title').text)

        self.textblock.show_title = True
        self.textblock.reindexObject(idxs=['id'])  # reindex metadata
        transaction.commit()
        browser.reload()

        # show_title is True => show block title
        self.assertEquals(['2.1.1 First things first'],
                          browser.css('.result .title').text)

    @browsing
    def test_title_is_linked_with_reader(self, browser):
        self.textblock.text = keywords_html('Foo')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(
            '{}/@@book_reader_view'.format(self.textblock.absolute_url()),
            browser.find('2.1.1 First things first').attrib['href'])

    @browsing
    def test_keywords_are_shown_foreach_result(self, browser):
        self.textblock.text = keywords_html('Foo', 'Bar', 'Baz')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['Bar,', 'Baz,', 'Foo'],
                          browser.css('.result-keywords span').text)

        self.assertEquals(['Foo'],
                          browser.css('.result-keywords b').text)

    @browsing
    def test_no_duplicate_keywords_in_result(self, browser):
        self.textblock.text = keywords_html('Foo', 'Bar', 'Foo')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(['Bar,', 'Foo'],
                          browser.css('.result-keywords span').text)

    @browsing
    def test_result_location_is_shown(self, browser):
        self.textblock.text = keywords_html('Foo')
        self.textblock.reindexObject()
        transaction.commit()

        browser.login().open(self.example_book,
                             {'book_keywords': 'Foo'},
                             view='tabbedview_view-keywords/load')

        self.assertEquals(
            ['The Example Book', '2 Historical Background', '2.1 China'],
            browser.css('.result-location a').text)

        self.assertEquals(
            '{}/@@book_reader_view'.format(self.example_book.absolute_url()),
            browser.css('.result-location a').first.attrib['href'])

    def test_chapters_cache(self):
        view = self.example_book.restrictedTraverse('tabbedview_view-keywords')

        self.assertItemsEqual(
            [
                '/plone/the-example-book',
                '/plone/the-example-book/empty',
                '/plone/the-example-book/historical-background',
                '/plone/the-example-book/historical-background/china',
                ('/plone/the-example-book/historical-background/china/'
                 'first-things-first'),
                ('/plone/the-example-book/historical-background/china/'
                 'important-documents'),
                '/plone/the-example-book/introduction',
                '/plone/the-example-book/introduction/management-summary',
            ],
            view.chapters.keys())

        self.assertDictContainsSubset(
            {'reader_url': '{}/@@book_reader_view'.format(
                self.example_book.absolute_url()),
             'title': 'The Example Book',
             'position': 0},
            view.chapters['/plone/the-example-book'])
        self.assertIn('brain', view.chapters['/plone/the-example-book'])

        self.assertDictContainsSubset(
            {'reader_url': '{}/historical-background/@@book_reader_view'.format(
                self.example_book.absolute_url()),
             'title': '2 Historical Background',
             'position': 3},
            view.chapters['/plone/the-example-book/historical-background'])

    @browsing
    def test_only_search_for_results_in_this_book(self, browser):
        # Regression: when having the same keyword in multiple books
        # the keyword tab was broken because of unspecific query (no path).

        create(Builder('book textblock').titled('First Block')
               .within(self.example_book.empty)
               .having(text=keywords_html('Foo', 'Bar')))

        second_book = create(Builder('book').titled(u'Second Book'))
        second_chapter = create(Builder('chapter').titled(u'Second chapter')
                                .within(second_book))
        create(Builder('book textblock').titled(u'Second Block')
               .within(second_chapter)
               .having(text=keywords_html('Bar', 'Baz')))

        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Foo', 'Bar', ''],
            browser.css('select[name=book_keywords] option').text,
            'Only keywords from the current book should be selectable.')

        browser.login().visit(second_book, view='tabbedview_view-keywords')
        self.assertItemsEqual(
            ['Bar', 'Baz', ''],
            browser.css('select[name=book_keywords] option').text,
            'Only keywords from the current book should be selectable.')

        browser.login().open(self.example_book,
                             {'book_keywords': 'Bar'},
                             view='tabbedview_view-keywords/load')
        self.assertEquals(1, len(browser.css('.result')),
                          'Only results from the current book should be'
                          ' found.')

    @browsing
    def test_select2_translations_are_loaded(self, browser):
        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertEquals(
            ['++resource++ftw.book-select2/select2.js'],
            select2_javascripts(),
            'Expected no translation to be loaded for english.')

        self.set_language_settings('de', ['de'])
        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertIn(
            '++resource++ftw.book-select2/select2_locale_de.js',
            select2_javascripts())

        self.set_language_settings('de-ch', ['de-ch'], use_combined=True)
        browser.login().visit(self.example_book, view='tabbedview_view-keywords')
        self.assertIn(
            '++resource++ftw.book-select2/select2_locale_de.js',
            select2_javascripts())
