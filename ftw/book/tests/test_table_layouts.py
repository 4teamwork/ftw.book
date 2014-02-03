from Products.CMFCore.utils import getToolByName
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from unittest2 import TestCase

TOP = set(['border-top'])
BOTTOM = set(['border-bottom'])
LEFT = set(['border-left'])
RIGHT = set(['border-right'])
ALL = TOP | BOTTOM | LEFT | RIGHT
NONE = set()


def table_borders():
    table = browser.css('table').first
    cell = lambda cell: (cell.text, set(cell.classes) & ALL)
    row = lambda row: map(cell, row.cells)
    return map(row, table.rows)


class TestTableLayouts(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        portal_types = getToolByName(self.layer['portal'], 'portal_types')
        table_fti = portal_types['Table']
        table_fti.global_allow = True

    @browsing
    def test_grid_layout(self, browser):
        table = create(Builder('table')
                       .with_table((('Foo', 'Bar'),
                                    ('1', '2')))
                       .having(borderLayout='grid'))

        browser.login().visit(table, view='block_view')

        self.assertEquals(
            [[('Foo', ALL),
              ('Bar', ALL)],
             [('1', ALL),
              ('2', ALL)]],
            table_borders())

    @browsing
    def test_invisible_layout(self, browser):
        table = create(Builder('table')
                       .with_table((('Foo', 'Bar'),
                                    ('1', '2')))
                       .having(borderLayout='invisible'))

        browser.login().visit(table, view='block_view')

        self.assertEquals(
            [[('Foo', NONE),
              ('Bar', NONE)],
             [('1', NONE),
              ('2', NONE)]],
            table_borders())

    @browsing
    def test_fancy_listing_layout(self, browser):
        table = create(Builder('table')
                       .with_table((('Foo', 'Bar'),
                                    ('1', '2')))
                       .having(borderLayout='fancy_listing'))

        browser.login().visit(table, view='block_view')

        self.assertEquals(
            [[('Foo',  BOTTOM),
              ('Bar', BOTTOM)],
             [('1', BOTTOM),
              ('2', BOTTOM)]],
            table_borders())
