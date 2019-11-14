from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book.browser.toc_tree import BookTocTree
from plone.app.layout.navigation.navtree import buildFolderTree
from zope.publisher.browser import BrowserView
import os.path
import unicodedata


class KeywordsTab(BrowserView):

    template = ViewPageTemplateFile('templates/keywords.pt')
    results = ViewPageTemplateFile('templates/keywords_results.pt')

    def __call__(self):
        return self.template()

    @property
    def macros(self):
        return {'form': self.template.macros['main'],
                'results': self.results.macros['main']}

    def keywords(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'path': '/'.join(self.context.getPhysicalPath()),
                 'object_provides': 'ftw.book.interfaces.IBookTextBlock'}

        keywords = set()

        for brain in catalog(query):
            for keyword in brain.book_keywords:
                keywords.add(keyword)

        return sorted(keywords, key=self.normalize_lower_keyword)

    def normalize_lower_keyword(self, keyword):
        unicoded = keyword.decode('utf-8')
        normalized = unicodedata.normalize('NFKD', unicoded).encode('ascii',
                                                                    'ignore')
        return normalized.lower()

    def load(self):
        """Load data as json.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(self._get_load_query())
        brains = self._sort_brains(brains)
        results = map(self._prepare_item, brains)
        return self.render_results(results=results)

    def render_results(self, results):
        return self.results(results=results)

    @property
    def chapters(self):
        if getattr(self, '_chapters', None) is None:
            tree = buildFolderTree(self.context, query={
                'path': '/'.join(self.context.getPhysicalPath())})
            tree = BookTocTree()(tree)

            def flatten(node):
                yield node
                for nodes in map(flatten, node.get('children', [])):
                    for subnode in nodes:
                        yield subnode

            self._chapters = {}
            for position, node in enumerate(flatten(tree)):
                brain = node['item']
                if node['toc_number']:
                    title = ' '.join((node['toc_number'], brain.Title))
                else:
                    title = brain.Title

                self._chapters[brain.getPath()] = {
                    'brain': brain,
                    'title': title,
                    'position': position,
                    'reader_url': '%s/@@book_reader_view' % brain.getURL()}

        return self._chapters


    def get_language(self):
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")

        return aq_inner(self.context).Language() or portal_state.default_language()

    def _prepare_item(self, brain):
        keywords = sorted(set(brain.book_keywords),
                          key=lambda item: item.lower())

        return {'brain': brain,
                'title': self._title_of_brain(brain),
                'location': self._location_for_brain(brain),
                'keywords': tuple(keywords)}

    def _location_for_brain(self, brain):
        book_path = '/'.join(self.context.getPhysicalPath())
        relpath = brain.getPath()[len(book_path + '/'):]
        location = []

        while relpath:
            relpath = os.path.dirname(relpath)
            path = '/'.join((book_path, relpath)).rstrip('/')
            location.insert(0, self.chapters[path])

        return location

    def _title_of_brain(self, brain):
        path = brain.getPath()
        if path in self.chapters:
            return self.chapters[path]['title']
        else:
            return self.chapters[os.path.dirname(path)]['title']

    def _get_load_query(self):
        return {'path': '/'.join(self.context.getPhysicalPath()),
                'book_keywords': self.request.form.get('book_keywords'),
                'sort_on': 'getObjPositionInParent'}

    def _sort_brains(self, brains):
        def sort_key(brain):
            if brain.getPath() in self.chapters:
                return self.chapters[brain.getPath()]['position']
            else:
                return self.chapters[
                    os.path.dirname(brain.getPath())]['position']
        return sorted(brains, key=sort_key)
