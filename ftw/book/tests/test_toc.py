from ftw.book.tests import FunctionalTestCase
from ftw.book.tests import LOREM_ITEM
from ftw.book.toc import TableOfContents
from operator import methodcaller


class TestTableOfContents(FunctionalTestCase):

    def sample_objects(self):
        """Some sample objects of the example book for testing things with.
        """
        return map(self.example_book.restrictedTraverse, (
            '..',
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

    def test_html_heading(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEqual(
            [
                None,  # Plone site
                '<h1 class="toc1">The Example Book</h1>',
                '<h2 class="toc2">Introduction</h2>',
                None,  # Invisible Title
                '<h3 class="no-toc">Versioning</h3>',
                '<h3 class="toc3">Management Summary</h3>',
                '<h2 class="toc2">Historical Background</h2>',
                '<h3 class="toc3">China</h3>',
                '<h4 class="toc4">First things first</h4>',
                '<h4 class="toc4">Important Documents</h4>',
                '<h5 class="no-toc">Einfache Webseite</h5>',
            ],
            map(toc.html_heading, self.sample_objects()))

    def test_html_heading_with_additional_classes(self):
        toc = TableOfContents()
        self.assertEquals(
            '<h1 class="documentFirstHeading toc1">The Example Book</h1>',
            toc.html_heading(self.example_book,
                             classes=['documentFirstHeading']))

        self.assertEquals(
            '<h4 class="hiddenStructure toc4">Important Documents</h4>',
            toc.html_heading(self.listingblock,
                             classes=['hiddenStructure']))

    def test_html_heading_with_link(self):
        toc = TableOfContents()
        china = self.example_book.get('historical-background').china
        self.assertEquals(
            '<h3 class="toc3"><a href="{}">China</a></h3>'.format(
                china.absolute_url()),
            toc.html_heading(china, linked=True))

    def test_html_heading_escapes_title(self):
        toc = TableOfContents()
        chapter = self.example_book.introduction
        chapter.title = 'Protect from <b>XSS</b>.'

        self.assertEquals(
            '<h2 class="toc2">Protect from &lt;b&gt;XSS&lt;/b&gt;.</h2>',
            toc.html_heading(chapter))

    def test_prepend_headings(self):
        chapter = self.example_book.restrictedTraverse(
            'historical-background/china/important-documents')

        self.assertEquals(
            '<h2 class="hiddenStructure toc2">Introduction</h2>\n'
            '<h2 class="hiddenStructure toc2">Historical Background</h2>\n'
            '<h3 class="hiddenStructure toc3">China</h3>\n'
            '<h4 class="hiddenStructure toc4">First things first</h4>',
            TableOfContents().prepend_html_headings(chapter))

    def test_in_toc(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': False,
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
                obj.Title(): toc.in_toc(obj)
                for obj in self.sample_objects()
            })

    def test_in_Book(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': False,
                'The Example Book': True,
                'Introduction': True,
                'Invisible Title': True,
                'Versioning': True,
                'Management Summary': True,
                'Historical Background': True,
                'China': True,
                'First things first': True,
                'Important Documents': True,
                'Einfache Webseite': True,
            },
            {
                obj.Title(): toc.in_book(obj)
                for obj in self.sample_objects()
            })

    def test_visible(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': True,
                'The Example Book': True,
                'Introduction': True,
                'Invisible Title': False,
                'Versioning': True,
                'Management Summary': True,
                'Historical Background': True,
                'China': True,
                'First things first': True,
                'Important Documents': True,
                'Einfache Webseite': True,
            },
            {
                obj.Title(): toc.visible(obj)
                for obj in self.sample_objects()
            })

    def test_level(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': None,
                'The Example Book': 1,
                'Introduction': 2,
                'Invisible Title': 3,
                'Versioning': 3,
                'Management Summary': 3,
                'Historical Background': 2,
                'China': 3,
                'First things first': 4,
                'Important Documents': 4,
                'Einfache Webseite': 5,
            },
            {
                obj.Title(): toc.level(obj)
                for obj in self.sample_objects()
            })

    def test_index(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': None,
                'The Example Book': None,
                'Introduction': 1,
                'Invisible Title': None,
                'Versioning': None,
                'Management Summary': 1,
                'Historical Background': 2,
                'China': 1,
                'First things first': 1,
                'Important Documents': 2,
                'Einfache Webseite': None,
            },
            {
                obj.Title(): toc.index(obj)
                for obj in self.sample_objects()
            })

    def test_number(self):
        toc = TableOfContents()
        self.maxDiff = None
        self.assertEquals(
            {
                'Plone site': None,
                'The Example Book': None,
                'Introduction': '1',
                'Invisible Title': None,
                'Versioning': None,
                'Management Summary': '1.1',
                'Historical Background': '2',
                'China': '2.1',
                'First things first': '2.1.1',
                'Important Documents': '2.1.2',
                'Einfache Webseite': None,
            },
            {
                obj.Title(): toc.number(obj)
                for obj in self.sample_objects()
            })

    def test_book(self):
        toc = TableOfContents()
        self.assertEquals(self.example_book, toc.book(self.example_book))
        self.assertEquals(self.example_book, toc.book(self.listingblock))
        self.assertEquals(None, toc.book(self.portal))

    def test_parent_chapters(self):
        self.assertEquals(
            ['Historical Background', 'China', 'Important Documents'],
            map(methodcaller('Title'),
                TableOfContents().parent_chapters(
                    self.example_book.restrictedTraverse(
                        'historical-background/china'
                        '/{}'.format('/'.join(LOREM_ITEM.split('/')[-2:]))))))

        self.assertEquals(
            ['Historical Background', 'China'],
            map(methodcaller('Title'),
                TableOfContents().parent_chapters(
                    self.example_book.restrictedTraverse(
                        'historical-background/china/important-documents'))))

        self.assertEquals(
            ['Historical Background'],
            map(methodcaller('Title'),
                TableOfContents().parent_chapters(
                    self.example_book.restrictedTraverse(
                        'historical-background/china'))))
