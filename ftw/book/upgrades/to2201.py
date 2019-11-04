from ftw.book.subscribers import add_navigation_portlet
from ftw.upgrade import UpgradeStep
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter


class SetBookPortlets(UpgradeStep):

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        brains = catalog(portal_type='Book')
        for brain in brains:
            book = brain.getObject()
            manager = getUtility(IPortletManager, name='plone.leftcolumn')
            mapping = getMultiAdapter((book, manager),
                                  IPortletAssignmentMapping).__of__(book)
            path = '/'.join(book.getPhysicalPath())[
                len(book.portal_url.getPortalPath()):]
            navi = mapping.get('navigation')
            if navi and navi.root == path:
                continue
            add_navigation_portlet(book, None)
