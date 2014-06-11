from ftw.book.portlets import gotoparent
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
import logging
from Products.CMFCore.utils import getToolByName

LOG = logging.getLogger('ftw.book')


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

    try:
        manager = getUtility(IPortletManager, name='plone.rightcolumn')

    except ComponentLookupError:
        # This happens when the plone site is removed.
        # In this case persistent utilites are already gone.
        # Reindexing is not necessary in this situation, since
        # everything will be gone.
        LOG.error('eventhandler.left_slot_portlets threw', exc_info=True)
        return

    assignable = getMultiAdapter((object_, manager,),
                                 ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def left_slot_portlets(object_):
    """ disable portlet inheritance at leftcolumn and
    add new navigation portlet
    """

    try:
        manager = getUtility(IPortletManager, name='plone.leftcolumn')

    except ComponentLookupError:
        # This happens when the plone site is removed.
        # In this case persistent utilites are already gone.
        # Reindexing is not necessary in this situation, since
        # everything will be gone.
        LOG.error('eventhandler.left_slot_portlets threw', exc_info=True)
        return

    assignable = getMultiAdapter((object_, manager,),
                                 ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
    mapping = getMultiAdapter((object_, manager),
                              IPortletAssignmentMapping).__of__(object_)

    if 'navigation' in mapping.keys():
        del mapping['navigation']

    if 'go-to-parent-portlet' not in mapping.keys():
        mapping['go-to-parent-portlet'] = gotoparent.Assignment()

    portal_url = getToolByName(object_, 'portal_url')
    relative_path = '/'.join(object_.getPhysicalPath())[
        len(portal_url.getPortalPath()):]

    mapping['navigation'] = navigation.Assignment(
        root=relative_path,
        topLevel=0,
        includeTop=1)
