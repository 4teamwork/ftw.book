from Products.CMFCore.utils import getToolByName
from ftw.book.tests import FunctionalTestCase
from ftw.book.tests import LOREM_ITEM
from plone.indexer.interfaces import IIndexer
from zope.component import getMultiAdapter


class TestShowInTocIndexer(FunctionalTestCase):

    def test(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        objects = map(self.example_book.restrictedTraverse, (
            '',
            'introduction',
            'introduction/invisible-title',
            'introduction/versioning',
            'introduction/management-summary',
            'historical-background',
            'historical-background/china',
            'historical-background/china/first-things-first',
            'historical-background/china/important-documents',
            LOREM_ITEM,
        ))

        self.assertEquals(
            {
                'The Example Book': True,
                'Introduction': True,
                'Invisible Title': False,
                'Versioning': False,
                'Management Summary': True,
                'Historical Background': True,
                'China': True,
                'First things first': True,
                'Important Documents': True,
                'Einfache Webseite': False,
            },
            {
                obj.Title(): getMultiAdapter((obj, catalog),
                                             IIndexer, name='show_in_toc')()
                for obj in objects
            })
