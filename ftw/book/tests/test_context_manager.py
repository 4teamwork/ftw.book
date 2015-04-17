from ftw.book.layer import providing_book_layers
from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from unittest2 import TestCase
from zope.interface import directlyProvidedBy


class TestContextManager(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_context_manager_adds_book_layers(self):
        thelist = list(directlyProvidedBy(self.portal.REQUEST))

        with providing_book_layers(self.portal, self.portal.REQUEST):
            diff = [it for it in list(
                    directlyProvidedBy(self.portal.REQUEST)) if it not in thelist]

            self.assertEquals(
                ['<InterfaceClass ftw.book.interfaces.IWithinBookLayer>'],
                [str(item) for item in diff])

        self.assertEquals(thelist,
                          list(directlyProvidedBy(self.portal.REQUEST)))
