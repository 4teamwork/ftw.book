from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.book import _
from ftw.book.helpers import BookHelper
from ftw.pdfgenerator.html2latex.subconverters.table import TableConverter
from plone.app.layout.viewlets import ViewletBase
from simplelayout.base import viewlets
import re


class SimpleLayoutListingViewlet(viewlets.SimpleLayoutListingViewlet):

    render = ViewPageTemplateFile('listing.pt')
    helper = BookHelper()

    def get_valid_parent_h_tags(self):
        return self.helper.generate_valid_hierarchy_h_tags(self.context)


class TableValidationViewlet(ViewletBase):

    render = ViewPageTemplateFile('table_validation.pt')

    def __init__(self, *args, **kwargs):
        super(TableValidationViewlet, self).__init__(*args, **kwargs)
        self.errors = None

    def update(self):
        self.errors = self._validate()

    def _validate(self):
        errors = set()
        errors = self._validate_tables(errors)
        return errors

    def _validate_tables(self, errors):
        xpr = re.compile(TableConverter.pattern, re.DOTALL)
        start = 0

        html = self.context.getText()

        while True:
            match = xpr.search(html, start)
            if not match:
                return errors

            start = match.end()
            errors = self._validate_table_width(html, match, errors)

    def _validate_table_width(self, html, match, errors):
        table = TableConverter(None, match, html)
        table.parse()

        for column in table.columns:
            if not column.get_width():
                errors.add(
                    _(u'table_width_validation_warning',
                      u'Please specify the width of the table ' +
                      u'columns / cells.'))
                return errors

        return errors
