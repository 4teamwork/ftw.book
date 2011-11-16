import unittest2 as unittest
import doctest
from plone.testing import layered
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('bookview.txt'),
                layer=FTW_BOOK_INTEGRATION_TESTING),
        layered(doctest.DocFileSuite('navigation.txt'),
                layer=FTW_BOOK_INTEGRATION_TESTING),
    ])
    return suite
