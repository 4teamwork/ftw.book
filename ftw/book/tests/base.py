from ftw.book.latex.defaultlayout import IDefaultBookLayout
from ftw.book.latex.layouts import get_layout_behavior_registration
from ftw.book.testing import LanguageSetter
from ftw.book.tests import export
from ftw.pdfgenerator.config import DefaultConfig
from plone.app.testing import applyProfile
from plone.browserlayer.layer import mark_layer
from plone.mocktestcase.dummy import Dummy
from unittest import TestCase
from zope.dottedname.resolve import resolve
import os


class PDFGeneratorTestConfig(DefaultConfig):

    remove_build_directory = False

    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def get_build_directory(self):
        return self.path


class PDFDiffTestCase(TestCase, LanguageSetter):

    # The path to the book object relative to the plone site root.
    book_object_path = 'example-book'

    # The relative path to the expected PDF file.
    # The path is relative to the subclassing TestCase class.
    expected_result = None

    # List additional generic setup profiles, which will be applied
    # while the layout layer already is on the request.
    # This allows to directly set layout field values using ftw.inflator
    # content creation.
    profiles = ['ftw.book.tests:examplecontent']

    # The book_layout_layer is the interface of the layout behavior.
    book_layout_layer = IDefaultBookLayout

    # The result_dir_name is the directory name in parts/test where the
    # resulting PDF and the diff is saved.
    result_dir_name = 'test_book_export'

    def condition(self):
        return os.environ.get('SKIP_BOOK_EXPORTS', '').strip().lower() != 'true'

    def setUp(self):
        if self._is_base_test() or not self.condition():
            return

        self.validate()
        self.resultdir = self.get_test_result_directory()

        from ftw.book import tests
        self.booksdir = os.path.join(os.path.dirname(tests.__file__), 'books')

        request = self.layer['portal'].REQUEST
        mark_layer(None, Dummy(request=request))

        # configure language to german, since the test book is german
        self.set_language_settings('de', ['de'])

        self.install_profiles()
        book = self.get_book_object()
        self.enable_layout(book)
        self.configure_layout(book)

        expectation = self.get_absolute_path(self.expected_result)
        filenamebase, _ext = os.path.splitext(os.path.basename(expectation))
        build_dir = os.path.join(self.resultdir, '%s_build' % filenamebase)
        self.config = PDFGeneratorTestConfig(build_dir)
        self.layer['portal'].getSiteManager().registerUtility(self.config)

    def tearDown(self):
        if self._is_base_test() or not self.condition():
            return

        self.layer['portal'].getSiteManager().unregisterUtility(self.config)

    def validate(self):
        name = type(self).__name__

        self.assertTrue(
            self.book_object_path,
            '%s has no book_object_path set. book_object_path should point'
            ' to the ftw.book Book object relative to the Plone site root.' %
            name)

        self.assertTrue(
            self.expected_result,
            '%s ahs no expected_result set. expected_result should be a path'
            ' relative to the test_*.py you are writing. It should point to'
            ' .pdf file which will be diffed to the resulting PDF.')

    def get_test_result_directory(self):
        assert os.getcwd().endswith('/parts/test'), \
            'Assumed the working directory is .../parts/test, ' \
            'but it is %s' % os.getcwd()

        expectation = self.get_absolute_path(self.expected_result)
        filenamebase, _ext = os.path.splitext(os.path.basename(expectation))

        if self.result_dir_name not in os.listdir('.'):
            os.mkdir(self.result_dir_name)
            return os.path.abspath(self.result_dir_name)

        files_to_delete = filter(lambda name: name.startswith(filenamebase),
                                 os.listdir(self.result_dir_name))

        if files_to_delete:
            os.system('rm -r %s/%s*' % (self.result_dir_name, filenamebase))

        return os.path.abspath(self.result_dir_name)

    def install_profiles(self):
        """Installes additional generic setup profile.
        """
        portal = self.layer['portal']

        self.layer['load_zcml_string'](
            '<configure>'
            '  <include package="ftw.book.tests" file="examplecontent.zcml" />'
            '</configure>')

        for profile in self.profiles:
            applyProfile(portal, profile)

    def enable_layout(self, book):
        book.latex_layout = self.book_layout_layer.__identifier__
        get_layout_behavior_registration(book)

    def configure_layout(self, book):
        pass

    def get_absolute_path(self, path):
        """Makes a path relative to the test case (self) absolute.
        """
        if path.startswith('/'):
            return path

        else:
            return os.path.join(
                    os.path.dirname(resolve(self.__module__).__file__),
                    path)

    def get_book_object(self):
        obj = self.layer['portal'].get(self.book_object_path)
        self.assertTrue(
            obj,
            'Could not find book object with path %s. IDs on portal %s' % (
                self.book_object_path,
                str(self.layer['portal'].contentIds())))
        return obj

    def _is_base_test(self):
        """Detect that the class was not subclassed so we can skip the tests.
        """
        return type(self) == PDFDiffTestCase

    def test_book_export(self):
        if self._is_base_test() or not self.condition():
            return

        expectation = self.get_absolute_path(self.expected_result)
        filenamebase, _ext = os.path.splitext(os.path.basename(expectation))

        book_obj = self.get_book_object()
        target = os.path.join(self.resultdir, '%s.pdf' % filenamebase)
        export.export_pdf(book_obj, target)

        # expectation = os.path.join(self.booksdir, '%s.pdf' % filenamebase)
        difference = os.path.join(self.resultdir,
                                  '%s-diff.pdf' % filenamebase)
        failed_pages = export.diff_pdfs(target, expectation, difference)

        self.assertEqual(
            len(failed_pages), 0,

            '\n'.join((
                    'The built PDF does not match the expected PDF.',
                    'Differing page(s): %s' % ', '.join(
                        map(str, sorted(failed_pages))),
                    'Result PDF:        %s' % target,
                    'Expected PDF:      %s' % expectation,
                    'Diff PDF:          %s' % difference)))
