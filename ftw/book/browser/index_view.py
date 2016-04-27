from ftw.book.browser.toc_tree import BookTocTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView


class IndexView(BrowserView):

    template = ViewPageTemplateFile('templates/index_view.pt')

    def __init__(self, *args, **kwargs):
        super(IndexView, self).__init__(*args, **kwargs)
        self.tree = None

    def __call__(self):
        context = self.context

        query = self._build_query()

        strategy = DepthNavTreeStrategy(self.context.getWeb_toc_depth())
        raw_tree = buildFolderTree(
            context, obj=context, query=query, strategy=strategy)
        toc_tree = BookTocTree()
        tree = toc_tree(raw_tree)
        self.tree = tree
        return self.template()

    def _build_query(self):
        query = {
            'path': '/'.join(self.context.getPhysicalPath())}

        portal_properties = getToolByName(self.context, 'portal_properties')
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        blacklist = navtree_properties.getProperty('metaTypesNotToList', ())
        all_types = portal_catalog.uniqueValuesFor('portal_type')
        query['portal_type'] = [t for t in all_types if t not in blacklist]

        return query


class DepthNavTreeStrategy(NavtreeStrategyBase):

    def __init__(self, bottomLevel):
        self.bottomLevel = bottomLevel

    def subtreeFilter(self, node):
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        return True
