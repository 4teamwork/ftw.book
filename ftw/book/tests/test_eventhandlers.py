from ftw.book.interfaces import IBook
from ftw.book.content.book import Book
from plone.mocktestcase import MockTestCase
from zope.interface import directlyProvides
from Products.Archetypes.event import ObjectInitializedEvent
from ftw.book import eventhandler
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from mocker import ANY
from zope.interface import Interface


class TestEventhandler(MockTestCase):
    
    def test_events(self):
        request = self.create_dummy()
        manager = self.mocker.mock(count=False)
        self.expect(manager()).result(None)
        portal_url = self.mocker.mock(count=False)
        self.expect(portal_url.getPortalPath()).result(('','plone'))
        assignable = self.mocker.mock(count=False)
        mapping = self.mocker.mock(count=False)
        pers_mapping = dict()
        parent = self.create_dummy(title='parent',absolute_url=lambda:'http://nohost/plone/parent')
        book = self.mocker.mock(Book, count=False)
        self.expect(assignable.setBlacklistStatus(ANY, ANY)).result(None)
        self.expect(book.title).result("mybook")
        self.expect(book.aq_parent).result(parent)
        self.expect(book.getPhysicalPath()).result(('','plone','parent', 'mybook'))
        self.expect(book()).result(None)
        self.expect(book.portal_url).result(portal_url)
        directlyProvides(book, IBook)
        self.mock_utility(manager, IPortletManager, name="plone.leftcolumn")
        self.mock_utility(manager, IPortletManager, name="plone.rightcolumn")
        self.mock_adapter(mapping, IPortletAssignmentMapping, (Interface, Interface))
        self.mock_adapter(assignable, ILocalPortletAssignmentManager, (Interface, Interface))
        self.expect(assignable(ANY, ANY)).result(assignable)
        self.expect(mapping(ANY, ANY)).result(mapping)
        self.expect(mapping.__of__(ANY)).result(pers_mapping)
        self.replay()
        event = ObjectInitializedEvent(book, request)
        eventhandler.add_navigation_portlet(book, event)
        gtpp_ass = pers_mapping['go-to-parent-portlet']
        nav_ass = pers_mapping['navigation']
        self.assertEqual(gtpp_ass.title, 'Go To Parent Portlet')
        self.assertEqual(nav_ass.__dict__, {'name': u'', 'bottomLevel': 0, 'topLevel': 0,
         'currentFolderOnly': False, 'includeTop': 1, 'root': 'lone/parent/mybook'})
        self.assertEqual(nav_ass.title, u'Navigation')

