from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.pdfgenerator.interfaces import ILaTeXView
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
        self.default_layout_book = self.portal.restrictedTraverse(
            self.layer['default_layout_book_path'])

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def get_assembler(self, export_context=None):
        return getMultiAdapter(
            (export_context or self.example_book, self.request),
            IPDFAssembler)

    def get_latex_layout(self, export_context=None):
        return self.get_assembler(export_context).get_layout()

    def get_latex_view_for(self, context, export_context=None):
        return getMultiAdapter(
            (context, self.request, self.get_latex_layout(export_context)),
            ILaTeXView)

    def create_dummy(self, **kw):
        return Dummy(**kw)


class Dummy(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)
