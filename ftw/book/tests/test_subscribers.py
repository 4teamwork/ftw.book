from ftw.book import IS_PLONE_5
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestSubscribers(FunctionalTestCase):

    def setup_expected_nav_dict(self, expect_folder=False):
        if IS_PLONE_5:
            return {'bottomLevel': 0,
                    'currentFolderOnly': False,
                    'includeTop': 1,
                    'name': '',
                    'no_icons': False,
                    'no_thumbs': False,
                    'root_uid': IUUID(self.example_book),
                    'thumb_scale': None,
                    'topLevel': 0}
        else:
            root = '/the-example-book'
            if expect_folder:
                root = '/the-folder/the-example-book'
            return {'name': '',
                    'bottomLevel': 0,
                    'topLevel': 0,
                    'currentFolderOnly': False,
                    'includeTop': 1,
                    'root': root}

    def test_standard_portlet_configuration(self):
        self.maxDiff = None
        navigation = self.setup_expected_nav_dict()

        self.assertEquals(
            {'plone.rightcolumn': {
                'assignments': {},
                'blacklist_status': True},
             'plone.leftcolumn': {
                 'assignments': {
                     'navigation': navigation,
                     'go-to-parent-portlet': {}},
                 'blacklist_status': True}},
            self.get_portlets_config(self.example_book))

    def test_path_in_navi_portletd_updated_when_moving(self):
        # TODO: in plone5 the assertion does not tell us anything really
        self.grant('Manager')
        folder = create(Builder('folder').titled(u'The Folder'))
        example_book_id = self.example_book.getId()
        folder.manage_pasteObjects(
                self.portal.manage_cutObjects(example_book_id))
        navigation = self.setup_expected_nav_dict(expect_folder=True)

        self.assertEquals(
            {'plone.rightcolumn': {
                'assignments': {},
                'blacklist_status': True},
             'plone.leftcolumn': {
                 'assignments': {
                     'navigation': navigation,
                     'go-to-parent-portlet': {}},
                 'blacklist_status': True}},
            self.get_portlets_config(folder.get(example_book_id)))

    def get_portlets_config(self, book):
        return {name: self.dump_manager(book, name)
                for name in ('plone.leftcolumn', 'plone.rightcolumn')}

    def dump_manager(self, context, manager_name):
        manager = getUtility(IPortletManager, name=manager_name)
        assignable = getMultiAdapter((context, manager),
                                     ILocalPortletAssignmentManager)
        mapping = getMultiAdapter((context, manager),
                                  IPortletAssignmentMapping).__of__(context)
        return {
            'blacklist_status': assignable.getBlacklistStatus(
                CONTEXT_CATEGORY),
            'assignments': {key: self.dump_assignment(value)
                            for key, value in mapping.items()}}

    def dump_assignment(self, assignment):
        str(assignment)  # triggers database sync
        return dict([(key, value) for (key, value) in vars(assignment).items()
                     if not key.startswith('_')])
