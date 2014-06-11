from Products.CMFCore.utils import getToolByName
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestHTMLBlockViewOutsideOfBook(TestCase):
    layer = FTW_BOOK_FUNCTIONAL_TESTING

    @browsing
    def test_block_view_outside_of_book(self, browser):
        ttool = getToolByName(self.layer['portal'], 'portal_types')
        ttool['ContentPage'].allowed_content_types += ('HTMLBlock',)

        page = create(Builder('content page'))
        htmlblock = create(Builder('htmlblock')
                           .titled('HTML Block')
                           .having(showTitle=True,
                                   text='<p id="html-block-text">The Text</p>')
                           .within(page))

        browser.visit(htmlblock)
        self.assertEquals(page, browser.context,
                          'HTMLBlock should redirect to container.')

        self.assertEquals('HTML Block',
                          browser.css('.simplelayout-block-wrapper h2').first.text)
        self.assertEquals('The Text', browser.css('#html-block-text').first.text)
