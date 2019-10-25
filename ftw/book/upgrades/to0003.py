from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides


def run_upgrades(setup):
    migrate_chapter_classes(setup)
    remove_old_chapter_actions(setup)
    set_book_layout(setup)


def remove_fti_action(setup, portal_type, action_id):
    """Remove the action identified by ``action_id`` from
    the FTI identified by ``portal_type``.
    """
    pt = getToolByName(setup, 'portal_types')
    fti = pt[portal_type]

    actions = []
    for action in fti._actions:
        if action.id != action_id:
            actions.append(action)
    fti._actions = tuple(actions)


def migrate_chapter_classes(setup):
    from simplelayout.base.interfaces import ISimpleLayoutBlock
    from ftw.book.content.chapter import Chapter
    catalog = getToolByName(setup, 'portal_catalog')
    brains = catalog(portal_type='Chapter')

    for brain in brains:
        obj = brain.getObject()
        obj.__class__ = Chapter
        alsoProvides(obj, ISimpleLayoutBlock)


def remove_old_chapter_actions(setup):
    remove_fti_action(setup, 'Chapter', 'edit-toggle')
    remove_fti_action(setup, 'Chapter', 'metadata')
    remove_fti_action(setup, 'Chapter', 'references')
    remove_fti_action(setup, 'Chapter', 'preview')
    remove_fti_action(setup, 'Chapter', 'history')


def set_book_layout(setup):
    catalog = getToolByName(setup, 'portal_catalog')

    brains = catalog(portal_type='Book')
    for brain in brains:
        obj = brain.getObject()
        obj.setLatex_layout(
            'ftw.book.latex.defaultlayout.IDefaultBookLayoutSelectionLayer')
