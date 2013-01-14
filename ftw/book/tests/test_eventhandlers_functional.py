from ftw.book.testing import FTW_BOOK_FUNCTIONAL_TESTING
from unittest2 import TestCase
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
import transaction

class TestEventhandlersFunctional(TestCase):

    layer = FTW_BOOK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.portal.invokeFactory('Folder', 'folder-1')
        self.portal.invokeFactory('Folder', 'folder-2')
        transaction.commit()

    def create_book(self):
        self.browser.open(self.portal.absolute_url()+'/folder-1/createObject?type_name=Book')
        self.browser.getControl(name="title").value = "Hans Peter"
        self.browser.getControl(name="form.button.save").click()


    def _auth(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))


    def get_portlet(self, obj):
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = getMultiAdapter((obj, manager),
                              IPortletAssignmentMapping).__of__(obj)
        return mapping['navigation']

    def test_move_book(self):
        self._auth()
        self.create_book()
        self.browser.getLink("Cut").click()
        self.browser.open(self.portal.absolute_url()+'/folder-2')
        self.browser.getLink("Paste").click()
        self.browser.open(self.browser.url+'/hans-peter')
        obj = self.portal['folder-2']['hans-peter']
        portlet = self.get_portlet(obj)
        self.assertEqual(portlet.root, '/folder-2/hans-peter')

    def test_copy_book(self):
        self._auth()
        self.create_book()
        self.browser.getLink("Copy").click()
        self.browser.open(self.portal.absolute_url()+'/folder-2')
        self.browser.getLink("Paste").click()
        self.browser.open(self.browser.url+'/hans-peter')
        obj = self.portal['folder-2']['hans-peter']
        portlet = self.get_portlet(obj)
        self.assertEqual(portlet.root, '/folder-2/hans-peter')

    def test_after_creation(self):
        self._auth()
        self.create_book()
        obj = self.portal['folder-1']['hans-peter']
        portlet = self.get_portlet(obj)
        self.assertEqual(portlet.root, '/folder-1/hans-peter')
