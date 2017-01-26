from Products.CMFCore.utils import getToolByName
from ftw.book import subscribers


def update_navigation(context):
    """updates navigation portlets for existing dossiers"""
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type="Book")
    for brain in brains:
        obj = brain.getObject()
        subscribers.right_slot_portlets(obj)
        subscribers.left_slot_portlets(obj)
