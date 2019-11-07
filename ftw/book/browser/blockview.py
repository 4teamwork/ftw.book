from ftw.book.toc import TableOfContents
from ftw.htmlblock.browser.htmlblock import HtmlBlockView
from ftw.pdfgenerator.html2latex.subconverters.table import TableConverter
from ftw.simplelayout.contenttypes.browser.filelistingblock import FileListingBlockView
from ftw.simplelayout.contenttypes.browser.textblock import TextBlockView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import re


class BookBlockMixin:
    book_template = ViewPageTemplateFile('templates/titled_block_view.pt')
    content_field_for_table_width_check = None

    def __call__(self, prepend_html_headings=False):
        self.prepend_html_headings = prepend_html_headings
        return self.book_template()

    @property
    def block_title(self):
        return TableOfContents().html_heading(
            self.context,
            linked=False,
            tagname='h2',
            prepend_html_headings=self.prepend_html_headings)

    def has_tables_with_missing_widths(self):
        if self.content_field_for_table_width_check is None:
            return

        value = getattr(self.context, self.content_field_for_table_width_check, '')
        if not value:
            return False

        return self._html_has_tables_with_missing_length(
            getattr(value, 'output', value))

    def _html_has_tables_with_missing_length(self, html):
        xpr = re.compile(TableConverter.pattern, re.DOTALL)
        start = 0

        while True:
            match = xpr.search(html, start)
            if not match:
                return False

            start = match.end()
            if self._table_has_missing_lengths(html, match):
                return True

        return False

    def _table_has_missing_lengths(self, html, match):
        table = TableConverter(None, match, html)
        table.parse()

        for column in table.columns:
            if not column.get_width():
                return True
        return False


class BookChapterView(BrowserView):

    def __call__(self, prepend_html_headings=False):
        self.prepend_html_headings = prepend_html_headings
        return self.index()

    @property
    def block_title(self):
        return TableOfContents().html_heading(
            self.context,
            tagname='h2',
            linked=True,
            prepend_html_headings=self.prepend_html_headings)


class BookTextBlockView(BookBlockMixin, TextBlockView):
    teaser_url = None
    content_field_for_table_width_check = 'text'


class BookFileListingBlockView(BookBlockMixin, FileListingBlockView):

    def render_table(self, ignore_columns=()):
        self.ignored_columns = ignore_columns
        return super(BookFileListingBlockView, self).render_table()

    def _filtered_columns(self):
        columns = super(BookFileListingBlockView, self)._filtered_columns()
        for column in columns:
            if column['column'] not in self.ignored_columns:
                yield column


class HTMLBlockView(BookBlockMixin, HtmlBlockView):
    content_field_for_table_width_check = 'content'
