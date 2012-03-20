from ftw.book.helpers import BookHelper
from ftw.book.interfaces import IBook
from plone.mocktestcase import MockTestCase
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.interface import directlyProvides


class TestUnitBookHelper(MockTestCase):
    """ Unittests for helper methods in BookHelper Class
    """

    def setUp(self):
        """ Setup test environment

        book
        |
        --- chapter1
        |
        --- chapter2
            |
            ---chapter3
            |  |
            |  ---chapter5
            |  |
            |  ---image
            |  |
            |  ---paragraph1
            |  |
            |  ---paragraph2
            |
            ---chapter4
        """

        # Helper object
        self.helper = BookHelper()

        #  Siteroot
        self.root = self.create_dummy()
        directlyProvides(self.root, IPloneSiteRoot)

        #  Book
        self.book = self.create_dummy()
        directlyProvides(self.book, [IBook, IFolderish])
        self.book = self.mocker.proxy(self.book, spec=False, count=False)
        self.expect(self.book.__parent__).result(self.root)
        self.expect(self.book.Title()).result('Book')

        # Childs of book
        self.chapter1 = self.create_dummy()
        directlyProvides(self.chapter1, IFolderish)
        self.chapter1 = self.mocker.proxy(
            self.chapter1, spec=False, count=False)
        self.expect(self.chapter1.__parent__).result(self.book)
        self.expect(self.chapter1.Title()).result('Chapter1')
        self.expect(self.chapter1.portal_type).result('Chapter')
        self.chapter2 = self.create_dummy()
        directlyProvides(self.chapter2, IFolderish)
        self.chapter2 = self.mocker.proxy(
            self.chapter2, spec=False, count=False)
        self.expect(self.chapter2.__parent__).result(self.book)
        self.expect(self.chapter2.Title()).result('Chapter2')
        self.expect(self.chapter2.portal_type).result('Chapter')

        #  Childs of chapter 2
        self.chapter3 = self.create_dummy()
        directlyProvides(self.chapter3, IFolderish)
        self.chapter3 = self.mocker.proxy(
            self.chapter3, spec=False, count=False)
        self.expect(self.chapter3.__parent__).result(self.chapter2)
        self.expect(self.chapter3.Title()).result('Chapter3')
        self.expect(self.chapter3.portal_type).result('Chapter')
        self.chapter4 = self.create_dummy()
        directlyProvides(self.chapter4, IFolderish)
        self.chapter4 = self.mocker.proxy(
            self.chapter4, spec=False, count=False)
        self.expect(self.chapter4.__parent__).result(self.chapter2)
        self.expect(self.chapter4.Title()).result('Chapter4')
        self.expect(self.chapter4.portal_type).result('Chapter')

        #  Childs of chapter 3
        self.chapter5 = self.create_dummy()
        directlyProvides(self.chapter5, IFolderish)
        self.chapter5 = self.mocker.proxy(
            self.chapter5, spec=False, count=False)
        self.expect(self.chapter5.__parent__).result(self.chapter3)
        self.expect(self.chapter5.Title()).result('Chapter5')
        self.expect(self.chapter5.portal_type).result('Chapter')
        self.image = self.mocker.mock(count=False)
        self.expect(self.image.__parent__).result(self.chapter3)
        self.expect(self.image.Title()).result('Image')
        self.expect(self.image.portal_type).result('Image')
        self.paragraph1 = self.mocker.mock(count=False)
        self.expect(self.paragraph1.__parent__).result(self.chapter3)
        self.expect(self.paragraph1.showTitle).result(True)
        self.expect(self.paragraph1.Title()).result('Paragraph1')
        self.expect(self.paragraph1.portal_type).result('Paragraph')
        self.paragraph2 = self.mocker.mock(count=False)
        self.expect(self.paragraph2.__parent__).result(self.chapter3)
        self.expect(self.paragraph2.__inner__).result(self.paragraph2)
        self.expect(self.paragraph2.showTitle).result(True)
        self.expect(self.paragraph2.Title()).result('Paragraph2')
        self.expect(self.paragraph2.title_or_id()).result('Paragraph2')
        self.expect(self.paragraph2.portal_type).result('Paragraph')

        # Folderish content
        self.expect(self.book.contentValues()).result(
            [self.chapter1, self.chapter2])
        self.expect(self.chapter1.contentValues()).result([])
        self.expect(self.chapter2.contentValues()).result(
            [self.chapter3, self.chapter4])
        self.expect(self.chapter3.contentValues()).result(
            [self.chapter5, self.image, self.paragraph1, self.paragraph2])
        self.expect(self.chapter4.contentValues()).result([])
        self.expect(self.chapter5.contentValues()).result([])

    def test_generate_title(self):
        """ Test generate title
        """
        self.replay()
        title = self.helper(self.paragraph2)
        self.assertTrue(title == '<h4>2.1.3 Paragraph2</h4>')

    def test_generate_valid_hierarchy_h_tags(self):
        """ Test generate valid hierarchy h tags
        """
        self.replay()
        tags = self.helper.generate_valid_hierarchy_h_tags(self.chapter3)
        self.assertTrue(
            tags == '<h1>Book</h1>' +
                    '<h2>Chapter2</h2>' +
                    '<h3>Chapter3</h3>')

    def test_get_folder_position(self):
        """ Test get folder position
        """
        self.replay()
        position = self.helper.get_folder_position(self.paragraph2)
        self.assertTrue(position == 3)

    def test_get_hierarchy_position(self):
        """ Test hierarchy position
        """
        self.replay()
        position = self.helper.get_hierarchy_position(self.paragraph2)
        self.assertTrue(position == 4)
