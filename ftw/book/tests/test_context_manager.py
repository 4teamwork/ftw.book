from ftw.book.layer import providing_book_layers
from ftw.book.tests import FunctionalTestCase
from zope.interface import directlyProvidedBy


class TestContextManager(FunctionalTestCase):

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
