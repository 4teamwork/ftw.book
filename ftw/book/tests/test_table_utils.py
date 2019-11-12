from unittest import TestCase
from ftw.book.table.utils import cleanup_standalone_html_tags



class TestCleanupStandaloneHTMLTags(TestCase):

    def test_br_is_cleaned_up(self):
        self.assertEquals(
            'foo<br/>bar',
            cleanup_standalone_html_tags('foo<br>bar'))

        self.assertEquals(
            'foo<br />bar',
            cleanup_standalone_html_tags('foo<br >bar'))

        self.assertEquals(
            'foo<br />bar',
            cleanup_standalone_html_tags('foo<br />bar'))

    def test_attributes_are_kept(self):
        self.assertEquals(
            'foo<br style="color:red;" />bar',
            cleanup_standalone_html_tags('foo<br style="color:red;" >bar'))

    def test_each_occurence_is_replaced(self):
        self.assertEquals(
            'foo<br/>bar<br/>baz',
            cleanup_standalone_html_tags('foo<br>bar<br>baz'))
