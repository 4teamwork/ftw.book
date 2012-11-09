from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.browser.toc_tree import BookTocTree
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.publisher.browser import BrowserView


class IndexView(BrowserView):

    template = ViewPageTemplateFile('index_view.pt')

    def __init__(self, *args, **kwargs):
        super(IndexView, self).__init__(*args, **kwargs)
        self.tree = None

    def __call__(self):
        context = self.context

        query = self._build_query()

        raw_tree = buildFolderTree(context, obj=context, query=query)
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
