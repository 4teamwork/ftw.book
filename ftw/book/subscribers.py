from Products.CMFCore.utils import getToolByName
from ftw.book import IS_PLONE_5
from ftw.book.portlets import gotoparent
from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
import logging

LOG = logging.getLogger('ftw.book')


def add_navigation_portlet(object_, event):
    """Adds a custom navigation Portlet for Buch
    """
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

    if IS_PLONE_5:
        # The new portlet assignment __init__ method does not accept root anymore
        # https://github.com/plone/plone.app.portlets/blob/40369fc1ce4d7eddc115695332694bd36995589f/plone/app/portlets/portlets/navigation.py#L148-L159
        obj_uid = IUUID(object_)
        mapping['navigation'] = navigation.Assignment(
            root_uid=obj_uid,
            topLevel=0,
            includeTop=1)
    else:
        portal_url = getToolByName(object_, 'portal_url')
        relative_path = '/'.join(object_.getPhysicalPath())[
            len(portal_url.getPortalPath()):]
        mapping['navigation'] = navigation.Assignment(
            root=relative_path,
            topLevel=0,
            includeTop=1)
