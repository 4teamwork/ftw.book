from ftw.book.behaviors.toc import IShowInToc
from ftw.book.browser.toc_tree import BookTocTree
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class IndexView(BrowserView):
    template = ViewPageTemplateFile('templates/index_view.pt')

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
        return {'path': '/'.join(self.context.getPhysicalPath()),
                'object_provides': IShowInToc.__identifier__}


class DepthNavTreeStrategy(NavtreeStrategyBase):

    def __init__(self, bottomLevel):
        self.bottomLevel = bottomLevel

    def subtreeFilter(self, node):
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        return True
