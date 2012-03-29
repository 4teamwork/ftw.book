from zope.publisher.browser import BrowserView
from plone.app.layout.navigation.navtree import buildFolderTree
from ftw.book.browser.toc_tree import BookTocTree
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IndexView(BrowserView):

    template = ViewPageTemplateFile('index_view.pt')

    def __call__(self):
        context = self.context
        query = {
            'path': '/'.join(context.getPhysicalPath())}
        raw_tree = buildFolderTree(context, obj=context, query=query)
        toc_tree = BookTocTree()
        tree = toc_tree(raw_tree)
        self.tree = tree
        return self.template()

