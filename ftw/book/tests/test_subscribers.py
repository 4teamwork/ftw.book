from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestSubscribers(FunctionalTestCase):

    def test_standard_portlet_configuration(self):
        self.assertEquals(
            {'plone.rightcolumn': {
                'assignments': {},
                'blacklist_status': True},
             'plone.leftcolumn': {
                 'assignments': {
                     'navigation': {'name': '',
                                    'bottomLevel': 0,
                                    'topLevel': 0,
                                    'currentFolderOnly': False,
                                    'includeTop': 1,
                                    'root': '/the-example-book'},
                     'go-to-parent-portlet': {}},
                 'blacklist_status': True}},
            self.get_portlets_config(self.example_book))

    def test_path_in_navi_portletd_updated_when_moving(self):
        self.grant('Manager')
        folder = create(Builder('folder').titled(u'The Folder'))
        book_id = self.example_book.getId()
        folder.manage_pasteObjects(self.portal.manage_cutObjects(book_id))

        self.assertEquals(
            {'plone.rightcolumn': {
                'assignments': {},
                'blacklist_status': True},
             'plone.leftcolumn': {
                 'assignments': {
                     'navigation': {'name': '',
                                    'bottomLevel': 0,
                                    'topLevel': 0,
                                    'currentFolderOnly': False,
                                    'includeTop': 1,
                                    'root': '/the-folder/the-example-book'},
                     'go-to-parent-portlet': {}},
                 'blacklist_status': True}},
            self.get_portlets_config(folder.get(book_id)))

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
