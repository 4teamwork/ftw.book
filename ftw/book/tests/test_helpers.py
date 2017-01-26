from ftw.book.behaviors.toc import IHideTitleFromTOC
from ftw.book.helpers import BookHelper
from ftw.book.tests import FunctionalTestCase


class TestBookHelper(FunctionalTestCase):

    def test_numbering(self):
        self.assertEqual(
            [
                '<h1>The Example Book</h1>',
                '<h2>1 Introduction</h2>',
                '<h3>1.1 Management Summary</h3>',
                '<h2>2 Historical Background</h2>',
                '<h3>2.1 China</h3>',
                '<h4>2.1.1 First things first</h4>',
            ],

            map(BookHelper(),
                map(self.portal.unrestrictedTraverse,
                    ['the-example-book',
                     'the-example-book/introduction',
                     'the-example-book/introduction/management-summary',
                     'the-example-book/historical-background',
                     'the-example-book/historical-background/china',
                     ('the-example-book/historical-background/china'
                      '/first-things-first')])))

    def test_linked_headings(self):
        book = self.portal.unrestrictedTraverse('the-example-book')
        chapter = book.unrestrictedTraverse('historical-background/china')

        self.assertEquals(
            '<h3><a href="{}/historical-background/china">2.1 China</a></h3>'
            .format(book.absolute_url()),
            BookHelper()(chapter, linked=True))

    def test_no_numbers_prepended_when_hide_from_toc_set(self):
        chapter = self.portal.unrestrictedTraverse(
            'the-example-book/introduction')

        self.maxDiff = None
        self.assertEqual(
            [{'id': 'invisible-title',
              'hide_from_toc': False,
              'show_title': False,
              'title': '<h3>Invisible Title</h3>'},

             {'id': 'versioning',
              'hide_from_toc': True,
              'show_title': True,
              'title': '<h3>Versioning</h3>'},

             {'id': 'management-summary',
              'hide_from_toc': False,
              'show_title': True,
              'title': '<h3>1.1 Management Summary</h3>'}],

            map(lambda obj: {
                'id': obj.getId(),
                'hide_from_toc': IHideTitleFromTOC(obj).hide_from_toc,
                'show_title': getattr(obj, 'show_title', None),
                'title': BookHelper()(obj)},
                chapter.objectValues()))

    def test_generate_valid_hierarchy_h_tags(self):
        context = self.portal.unrestrictedTraverse(
            'the-example-book/introduction/management-summary')
        self.assertEquals(
            '<h1>The Example Book</h1>'
            '<h2>Introduction</h2>'
            '<h3>Management Summary</h3>',
            BookHelper().generate_valid_hierarchy_h_tags(context))

    def test_get_hierarchy_position(self):
        context = self.portal.unrestrictedTraverse(
            'the-example-book/introduction/management-summary')
        self.assertEquals(3, BookHelper().get_hierarchy_position(context))
