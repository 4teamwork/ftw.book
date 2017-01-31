from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.pdfgenerator.interfaces import IPDFAssembler
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent
import transaction


class FunctionalTestCase(TestCase):
    layer = BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        notify(BeforeTraverseEvent(self.portal, self.request))
        self.example_book = self.portal.restrictedTraverse(
            self.layer['example_book_path'])

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def get_assembler(self):
        return getMultiAdapter((self.example_book, self.request),
                               IPDFAssembler)

    def get_latex_layout(self):
        return self.get_assembler().get_layout()
