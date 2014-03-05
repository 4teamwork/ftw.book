from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase
import transaction


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
