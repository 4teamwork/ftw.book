from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.book.helpers import BookHelper
from ftw.book.interfaces import IBook
from ftw.testing import MockTestCase
from mocker import ANY
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
            |  ---textblock1
            |  |
            |  ---textblock2
            |
            ---chapter4
        """
        super(TestUnitBookHelper, self).setUp()

        self._injection = {}

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
        self.mock_inject_settings(self.book)

        # Children of book
        self.chapter1 = self.create_dummy()
        directlyProvides(self.chapter1, IFolderish)
        self.chapter1 = self.mocker.proxy(
            self.chapter1, spec=False, count=False)
        self.expect(self.chapter1.__parent__).result(self.book)
        self.expect(self.chapter1.Title()).result('Chapter1')
        self.expect(self.chapter1.portal_type).result('Chapter')
        self.mock_inject_settings(self.chapter1)

        self.chapter2 = self.create_dummy()
        directlyProvides(self.chapter2, IFolderish)
        self.chapter2 = self.mocker.proxy(
            self.chapter2, spec=False, count=False)
        self.expect(self.chapter2.__parent__).result(self.book)
        self.expect(self.chapter2.Title()).result('Chapter2')
        self.expect(self.chapter2.portal_type).result('Chapter')
        self.mock_inject_settings(self.chapter2)

        #  Children of chapter 2
        self.chapter3 = self.create_dummy()
        directlyProvides(self.chapter3, IFolderish)
        self.chapter3 = self.mocker.proxy(
            self.chapter3, spec=False, count=False)
        self.expect(self.chapter3.__parent__).result(self.chapter2)
        self.expect(self.chapter3.Title()).result('Chapter3')
        self.expect(self.chapter3.portal_type).result('Chapter')
        self.mock_inject_settings(self.chapter3)

        self.chapter4 = self.create_dummy()
        directlyProvides(self.chapter4, IFolderish)
        self.chapter4 = self.mocker.proxy(
            self.chapter4, spec=False, count=False)
        self.expect(self.chapter4.__parent__).result(self.chapter2)
        self.expect(self.chapter4.Title()).result('Chapter4')
        self.expect(self.chapter4.portal_type).result('Chapter')
        self.mock_inject_settings(self.chapter4)

        #  Children of chapter 3
        self.chapter5 = self.create_dummy()
        directlyProvides(self.chapter5, IFolderish)
        self.chapter5 = self.mocker.proxy(
            self.chapter5, spec=False, count=False)
        self.expect(self.chapter5.__parent__).result(self.chapter3)
        self.expect(self.chapter5.Title()).result('Chapter5')
        self.expect(self.chapter5.portal_type).result('Chapter')
        self.mock_inject_settings(self.chapter5)

        self.image = self.mocker.mock(count=False)
        self.expect(self.image.__parent__).result(self.chapter3)
        self.expect(self.image.Title()).result('Image')
        self.expect(self.image.portal_type).result('Image')
        self.mock_inject_settings(self.image)

        self.textblock1 = self.mocker.mock(count=False)
        self.expect(self.textblock1.__parent__).result(self.chapter3)
        self.expect(self.textblock1.showTitle).result(True)
        self.expect(self.textblock1.Title()).result('Textblock1')
        self.expect(self.textblock1.title_or_id()).result('Textblock1')
        self.expect(self.textblock1.portal_type).result('Textblock')
        self.mock_inject_settings(self.textblock1, hideFromTOC=False)

        self.textblock2 = self.mocker.mock(count=False)
        self.expect(self.textblock2.__parent__).result(self.chapter3)
        self.expect(self.textblock2.__inner__).result(self.textblock2)
        self.expect(self.textblock2.showTitle).result(True)
        self.expect(self.textblock2.Title()).result('Textblock2')
        self.expect(self.textblock2.title_or_id()).result('Textblock2')
        self.expect(self.textblock2.portal_type).result('Textblock')
        self.mock_inject_settings(self.textblock2, hideFromTOC=False)

        # Folderish content
        self.expect(self.book.contentValues()).result(
            [self.chapter1, self.chapter2])
        self.expect(self.chapter1.contentValues()).result([])
        self.expect(self.chapter2.contentValues()).result(
            [self.chapter3, self.chapter4])
        self.expect(self.chapter3.contentValues()).result(
            [self.chapter5, self.image, self.textblock1, self.textblock2])
        self.expect(self.chapter4.contentValues()).result([])
        self.expect(self.chapter5.contentValues()).result([])

    def mock_inject_settings(self, mock, **settings):
        if mock not in self._injection:
            cache = self._injection[mock] = {'schema': self.stub()}
            schema = cache['schema']
            self.expect(mock.Schema()).result(schema).count(0, None)

            self.expect(schema.getField(ANY)).call(
                lambda name: cache.get(name, None))

        else:
            cache = self._injection[mock]

        for name, value in settings.items():
            field = self.stub()
            cache[name] = field
            self.expect(field.get(mock)).result(value)

    def test_generate_title(self):
        """ Test generate title
        """
        self.replay()

        self.assertEqual(self.helper(self.textblock1),
                         '<h4>2.1.2 Textblock1</h4>')
        self.assertEqual(self.helper(self.textblock2),
                         '<h4>2.1.3 Textblock2</h4>')

    def test_generate_title_respects_hideFromTOC(self):
        """ Test generate title
        """
        self.mock_inject_settings(self.textblock1, hideFromTOC=True)
        self.replay()

        # hideFromTOC is True
        self.assertEqual(self.helper(self.textblock1),
                         '<h4>Textblock1</h4>')
        self.assertEqual(self.helper(self.textblock2),
                         '<h4>2.1.2 Textblock2</h4>')

    def test_generated_title_result_is_consistent(self):
        self.mock_inject_settings(self.textblock1, hideFromTOC=True)
        self.replay()

        self.assertTrue(self.textblock1.Schema().getField(
                'hideFromTOC').get(self.textblock1))

        self.assertTrue(self.textblock1.Schema().getField(
                'hideFromTOC').get(self.textblock1))

        self.assertTrue(self.textblock1.Schema().getField(
                'hideFromTOC').get(self.textblock1))

        self.assertEqual(BookHelper()(self.textblock1),
                         '<h4>Textblock1</h4>')

        self.assertEqual(BookHelper()(self.textblock1),
                         '<h4>Textblock1</h4>')


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
        position = self.helper.get_folder_position(self.textblock2)
        self.assertTrue(position == 3)

    def test_get_hierarchy_position(self):
        """ Test hierarchy position
        """
        self.replay()
        position = self.helper.get_hierarchy_position(self.textblock2)
        self.assertTrue(position == 4)
