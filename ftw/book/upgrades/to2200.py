from Acquisition import aq_parent, aq_inner
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
import logging
from ftw.book.eventhandler import add_navigation_portlet
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter


LOG = logging.getLogger('ftw.book.upgrades')


class MakeBlocksSearchable(UpgradeStep):
    """In simplelayout the search behavior was changed:
    When a block is changed, the searchable text of the block is merged
    into the searchable text of the parent, so that the parent is found.
    The block is not listed in search results any more.

    We need hide the block types:
    - HTMLBlock
    - Remark
    - Table

    And we need to reindex tables (and their parents): the "data" of the
    table is now searchable.
    """

    def __call__(self):
        self.hide_block_types_from_searchresults()
        self.reindex_table_searchabletext_in_chapter()

    def hide_block_types_from_searchresults(self):
        LOG.info('Hide block types from search results.')
        self.setup_install_profile(
            'profile-ftw.book.upgrades:2200')

    def reindex_table_searchabletext_in_chapter(self):
        catalog = self.getToolByName('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='Table')

        title = 'Reindex table searchable text in parent chapter.'
        with ProgressLogger(title, brains) as step:

            for brain in brains:
                obj = self.portal.unrestrictedTraverse(brain.getPath())
                obj.reindexObject(idxs=['SearchableText'])
                parent = aq_parent(aq_inner(obj))
                parent.reindexObject(idxs=['SearchableText'])
                step()


class SetBookPortlest(UpgradeStep):

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
