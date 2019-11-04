from ftw.book.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestBook(FunctionalTestCase):

    @browsing
    def test_creating_book(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Book')

        browser.fill({'Title': 'The Book'}).submit()
        self.assertEquals(self.portal.absolute_url() + '/the-book/view',
                          browser.url)
        self.assertEquals(['The Book'],
                          browser.css('.documentFirstHeading').text)
