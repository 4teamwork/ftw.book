from contextlib import contextmanager
from ftw.book import IS_PLONE_5
from ftw.book.testing import BOOK_FUNCTIONAL_TESTING
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.interfaces import IPDFAssembler
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.uuid.interfaces import IUUID
from textwrap import dedent
from unittest import TestCase
from zope.component import getMultiAdapter
import difflib
import transaction


LOREM_ITEM = 'historical-background/china/important-documents/lorem.html'


class FunctionalTestCase(TestCase):
    layer = BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.example_book = self.portal.restrictedTraverse(
            self.layer['example_book_path'])
        self.default_layout_book = self.portal.restrictedTraverse(
            self.layer['default_layout_book_path'])

        self.htmlblock = self.example_book.restrictedTraverse(
            'introduction/an-html-block')
        self.listingblock = self.example_book.restrictedTraverse(
            'historical-background/china/important-documents')
        self.lorem_file = self.listingblock.restrictedTraverse(
            'lorem.html')
        self.table = self.example_book.unrestrictedTraverse(
            'historical-background/china/population')
        self.textblock = self.example_book.unrestrictedTraverse(
            'historical-background/china/first-things-first')
        self.textblock2 = self.example_book.unrestrictedTraverse(
            'introduction/management-summary')
        self.textblock3 = self.example_book.unrestrictedTraverse(
            'introduction/versioning')

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

    def get_latex_code(self, obj):
        got_latex = self.get_latex_layout(obj).render_latex_for(obj).strip()
        return got_latex.replace(IUUID(obj), 'XBlockUUIDX')

    def create_dummy(self, **kw):
        return Dummy(**kw)

    def assert_latex_code(self, obj, expected_latex_code):
        self.maxDiff = None
        self.assertMultiLineEqual(dedent(expected_latex_code).strip(),
                                  self.get_latex_code(obj))

    @contextmanager
    def assert_latex_diff(self, obj, expected_diff):
        latex_before = self.get_latex_code(obj)
        yield
        latex_after = self.get_latex_code(obj)
        got_diff = '\n'.join(difflib.unified_diff(
            latex_before.splitlines(),
            latex_after.splitlines(),
            fromfile='before.tex',
            tofile='after.tex',
            lineterm='')).strip()
        expected_diff = '\n'.join([line or ' ' for line
                                   in dedent(expected_diff).strip().split('\n')])

        if got_diff != expected_diff:
            raise AssertionError(
                ('Unexpected diff.\n'
                 'EXPECTED:\n{}\n\n'
                 'GOT:\n{}\n\n'
                 'Full LaTeX after the change:\n{}').format(expected_diff,
                                                            got_diff,
                                                            latex_after))


class Dummy(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)
