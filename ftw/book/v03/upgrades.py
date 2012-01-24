from Products.CMFCore.utils import getToolByName
from ftw.book.content.chapter import Chapter


def migrate_chapter_classes(setup):
    catalog = getToolByName(setup, 'portal_catalog')
    brains = catalog(portal_type='Chapter')

    for brain in brains:
        obj = brain.getObject()
        obj.__class__ = Chapter
