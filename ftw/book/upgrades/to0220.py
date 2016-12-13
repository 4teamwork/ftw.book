from Products.Archetypes.annotations import AT_ANN_STORAGE
from Products.Archetypes.annotations import getAnnotation
from Products.CMFCore.utils import getToolByName


_marker = object()


def migrate_book_storage(setup):
    """Migrate book metadata fields from AnnotationStorage to
    AttributeStorage.
    """

    catalog = getToolByName(setup, 'portal_catalog')
    brains = catalog(portal_type='Book')

    for brain in brains:
        _migrate_book(brain.getObject())


def _migrate_book(obj):
    fields = ['title', 'description', 'use_titlepage', 'use_toc',
              'use_lot', 'use_loi']

    ann = getAnnotation(obj)

    for name in fields:
        value = ann.getSubkey(AT_ANN_STORAGE, subkey=name,
                              default=_marker)

        if value is not _marker:
            obj.getField(name).set(obj, value)
