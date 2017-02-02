from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
import transaction


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


class TestTableLayouts(FunctionalTestCase):

    def setUp(self):
        super(TestTableLayouts, self).setUp()
        self.table = self.example_book.unrestrictedTraverse(
            'historical-background/china/population')

    @browsing
    def test_grid_layout(self, browser):
        self.table.border_layout = 'grid'
        transaction.commit()
        browser.login().visit(self.table, view='block_view')
        self.assertEquals(
            [[('Ranking', ALL), ('City', ALL), ('Population', ALL)],
             [('1', ALL), ('Guangzhou', ALL), ('44 mil 1', ALL)],
             [('2', ALL), ('Shanghai', ALL), ('35 mil', ALL)],
             [('3', ALL), ('Chongqing', ALL), ('30 mil', ALL)]],
            table_borders())

    @browsing
    def test_invisible_layout(self, browser):
        self.table.border_layout = 'invisible'
        transaction.commit()
        browser.login().visit(self.table, view='block_view')
        self.assertEquals(
            [[('Ranking', NONE), ('City', NONE), ('Population', NONE)],
             [('1', NONE), ('Guangzhou', NONE), ('44 mil 1', NONE)],
             [('2', NONE), ('Shanghai', NONE), ('35 mil', NONE)],
             [('3', NONE), ('Chongqing', NONE), ('30 mil', NONE)]],
            table_borders())

    @browsing
    def test_fancy_listing_layout(self, browser):
        self.table.border_layout = 'fancy_listing'
        transaction.commit()
        browser.login().visit(self.table, view='block_view')
        self.assertEquals(
            [[('Ranking', BOTTOM), ('City', BOTTOM), ('Population', BOTTOM)],
             [('1', BOTTOM), ('Guangzhou', BOTTOM), ('44 mil 1', BOTTOM)],
             [('2', BOTTOM), ('Shanghai', BOTTOM), ('35 mil', BOTTOM)],
             [('3', BOTTOM), ('Chongqing', BOTTOM), ('30 mil', BOTTOM)]],
            table_borders())
