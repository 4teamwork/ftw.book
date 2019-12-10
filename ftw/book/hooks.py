from Products.CMFCore.utils import getToolByName
from ftw.book.config import INDEXES
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import logging
import pkg_resources
import re


IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'
PROFILE_ID = 'profile-ftw.book:default'


def installed(site):
    add_catalog_indexes(site)


def uninstalled(site):
    remove_catalog_indexes(site)
    if IS_PLONE_5:
        clean_plone5_registry(site)


def clean_plone5_registry(site):
    registry = getUtility(IRegistry)

    types_not_searched = list(registry['plone.types_not_searched'])
    types_not_searched.remove('ftw.book.FileListingBlock')
    types_not_searched.remove('ftw.book.HtmlBlock')
    types_not_searched.remove('ftw.book.Table')
    types_not_searched.remove('ftw.book.TextBlock')
    registry['plone.types_not_searched'] = tuple(types_not_searched)

    displayed_types = list(registry['plone.displayed_types'])
    displayed_types.remove(u'ftw.book.Book')
    registry['plone.displayed_types'] = tuple(displayed_types)

    custom_attributes = registry['plone.custom_attributes']
    custom_attributes.remove(u'data-footnote')
    registry['plone.custom_attributes'] = custom_attributes

    content_css_entries = registry['plone.content_css']
    registry['plone.content_css'] = content_css_entries

    custom_plugins = registry['plone.custom_plugins']
    custom_plugins.remove(u'keyword|++resource++ftw.book-resources/tinymce/keyword-button-plugin.js')
    custom_plugins.remove(u'footnote|++resource++ftw.book-resources/tinymce/footnote-button-plugin.js')
    registry['plone.custom_plugins'] = custom_plugins

    tinymce_toolbar = registry['plone.toolbar']
    # this works unless the entries came first
    tinymce_toolbar = re.sub(r'\s*\|*\s*keyword\s*', '', tinymce_toolbar)
    tinymce_toolbar = re.sub(r'\s*\|*\s*footnote\s*', '', tinymce_toolbar)
    registry['plone.toolbar'] = tinymce_toolbar


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ftw.book')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = INDEXES
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def remove_catalog_indexes(context):
    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    for name, meta_type in INDEXES:
        if name in indexes:
            catalog.delIndex(name)
