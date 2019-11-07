from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from operator import attrgetter


class TestChapter(FunctionalTestCase):

    @browsing
    def test_creating_chapter(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book)
        factoriesmenu.add('Chapter')

        browser.fill({'Title': 'The Chapter'}).submit()
        self.assertEquals(self.example_book.absolute_url() + '/the-chapter/view',
                          browser.url)
        self.assertEquals(['The Chapter'],
                          browser.css('.documentFirstHeading').text)

    @browsing
    def test_subchapter_is_rendered_as_block_in_parent(self, browser):
        chapter = self.portal.restrictedTraverse(
            'the-example-book/historical-background')
        subchapter = chapter.china

        browser.login().visit(chapter)
        self.assertIn(
            u'<h2 class="toc3"><a href="{}">China</a></h2>'.format(
                subchapter.absolute_url()),
            map(attrgetter('outerHTML'), browser.css('.sl-block h2')))

        browser.css('#content-core').first.find('China').click()
        self.assertEquals(subchapter, browser.context)
