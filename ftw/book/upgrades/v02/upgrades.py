from Products.CMFCore.utils import getToolByName
from ftw.book import eventhandler


def update_navigation(context):
    """updates navigation portlets for existing dossiers"""
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="Book")
    for brain in brains:
        obj = brain.getObject()
        eventhandler.right_slot_portlets(obj)
        eventhandler.left_slot_portlets(obj)
