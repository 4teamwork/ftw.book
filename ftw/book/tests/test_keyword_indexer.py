from Products.CMFCore.utils import getToolByName
from ftw.book.browser.indexer import book_keywords
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from plone.app.textfield.value import RichTextValue
from plone.mocktestcase.dummy import Dummy
from unittest import TestCase


class TestUnitKeywords(TestCase):

    def test_extracts_keywords_from_text(self):
        html = '<p>Foo <span class="keyword" title="bar">Bar</span> Baz</p>'
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals(['bar'], book_keywords(obj)())

    def test_extracts_multiple_keywords(self):
        html = '\n'.join((
                '<p>',
                ' <span class="keyword" title="Foo">Foo</span>',
                ' <span class="keyword" title="barX">Bar</span>',
                ' <span class="keyword" title="Baz">Baz</span>',
                '</p>'))
        obj = Dummy(text=RichTextValue(html))

        self.assertEquals(['Foo', 'barX', 'Baz'],
                          book_keywords(obj)())

    def test_returns_empty_list_when_no_text_is_set(self):
        obj = Dummy(text=None)
        self.assertEquals([],
                          book_keywords(obj)())

    def test_does_not_include_empty_keyword_nodes(self):
        html = '\n'.join((
                '<p>',
                ' <span class="keyword" title="Foo">Foo</span>',
                ' <span class="keyword" title="">Bar</span>',
                ' <span class="keyword">Baz</span>',
                '</p>'))
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals(['Foo'], book_keywords(obj)())

    def test_strips_whitespace(self):
        html = '\n'.join((
                '<p>',
                ' <span class="keyword" title=" Foo Bar ">Foo Bar</span>',
                '</p>'))
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals(['Foo Bar'], book_keywords(obj)())

    def test_works_with_multiple_root_nodes(self):
        html = '\n'.join((
                '<span class="keyword" title="Foo">Foo</span>',
                '<span class="keyword" title="Bar">Bar</span>'))
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals(['Foo', 'Bar'], book_keywords(obj)())

    def test_unicode_umlauts(self):
        html = u'\n'.join((
                u'<p>',
                u' <span class="keyword" title="hall\xf6chen">Hi</span>',
                u'</p>'))
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals([u'hall\xf6chen'.encode('utf-8')],
                          book_keywords(obj)())

    def test_utf8_umlauts(self):
        html = u'\n'.join((
                u'<p>',
                u' <span class="keyword" title="hall\xf6chen">Hi</span>',
                u'</p>')).encode('utf-8')
        obj = Dummy(text=RichTextValue(html))
        self.assertEquals([u'hall\xf6chen'.encode('utf-8')],
                          book_keywords(obj)())


class TestKeywordIndex(FunctionalTestCase):

    def test_indexes_blocks(self):
        self.grant('Manager')
        html = '<p><span class="keyword" title="Foo">Foo</span></p>'
        block = create(Builder('book textblock')
                       .with_text(html)
                       .within(self.example_book.empty))

        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        rid = catalog.getrid(path='/'.join(block.getPhysicalPath()))
        index_data = catalog.getIndexDataForRID(rid)

        self.assertDictContainsSubset(
            {'book_keywords': ['Foo']},
            index_data)

    def test_keyword_metadata(self):
        html = '<p><span class="keyword" title="Foo">Foo</span></p>'
        block = create(Builder('book textblock')
                       .with_text(html)
                       .within(self.example_book.empty))

        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        brain = catalog({'path': '/'.join(block.getPhysicalPath())})[0]
        self.assertEquals(['Foo'],
                          brain.book_keywords)
