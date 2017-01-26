from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestChapter(FunctionalTestCase):

    @browsing
    def test_creating_chapter(self, browser):
        self.grant('Manager')
        browser.login().visit(self.example_book)
        factoriesmenu.add('Chapter')

        browser.fill({'Title': 'The Chapter'}).submit()
        self.assertEquals(self.example_book.absolute_url() + '/the-chapter/view',
                          browser.url)
        self.assertEquals('The Chapter', browser.css('h1').first.text)

    @browsing
    def test_subchapter_is_rendered_as_block_in_parent(self, browser):
        chapter = self.portal.restrictedTraverse(
            'the-example-book/historical-background')
        subchapter = chapter.china

        browser.login().visit(chapter)
        block, = browser.css('.simplelayout-block-wrapper')
        self.assertEquals(['2.1 China'], block.css('h3').text)

        block.find('2.1 China').click()
        self.assertEquals(subchapter, browser.context)
