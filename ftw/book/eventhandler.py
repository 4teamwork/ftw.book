from ftw.book.portlets import gotoparent
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter


def add_navigation_portlet(object_, event):
    """Adds a custom navigation Portlet for Buch
    """
    if 'portal_factory' in object_.getPhysicalPath():
        # do not run in portal_factory
        pass
    else:
        right_slot_portlets(object_)
        left_slot_portlets(object_)


def right_slot_portlets(object_):
    """ disable portlet inheritance at rightcolumn
    """
    manager = getUtility(IPortletManager, name='plone.rightcolumn')
    assignable = getMultiAdapter((object_, manager,),
                                 ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def left_slot_portlets(object_):
    """ disable portlet inheritance at leftcolumn and
    add new navigation portlet
    """
    manager = getUtility(IPortletManager, name='plone.leftcolumn')
    assignable = getMultiAdapter((object_, manager,),
                                 ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
    mapping = getMultiAdapter((object_, manager),
                              IPortletAssignmentMapping).__of__(object_)

    if 'navigation' in mapping.keys():
        del mapping['navigation']

    if not 'go-to-parent-portlet' in mapping.keys():
        mapping['go-to-parent-portlet'] = gotoparent.Assignment()

    relative_path = '/'.join(object_.getPhysicalPath())[
        len(object_.portal_url.getPortalPath()):]

    mapping['navigation'] = navigation.Assignment(
        root=relative_path,
        topLevel=0,
        includeTop=1)
