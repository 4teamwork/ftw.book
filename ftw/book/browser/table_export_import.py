from Products.CMFDiffTool.utils import safe_utf8
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book import _
from ftw.book.toc import TableOfContents
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from StringIO import StringIO
import csv


class TableExportImport(BrowserView):
    """ Provides functions to export or import tables.
    Output and input format is csv
    """

    def __call__(self):
        if self.request.get('export', None):
            return self.export_table()
        elif self.request.get('import', None):
            result = self.import_table()
            if result:
                return result
        return super(TableExportImport, self).__call__()

    @property
    def active_columns(self):
        context = aq_inner(self.context)
        columns = []
        for i, row in enumerate(context.getColumnProperties()):
            if row['active']:
                columns.append('column_%i' % i)
        return columns

    def get_column_options(self):
        context = aq_inner(self.context)
        options = []
        if len(context.getData()) == 0:
            return options
        options.append(('', ' - Bitte auswaehlen - '))
        first_row = context.getData()[0].copy()
        for i, row in enumerate(context.getColumnProperties()):
            key = 'column_%i' % i
            label = '%s (Spalte %i)' % (
                first_row[key],
                i + 1,
                )
            if row['active']:
                options.append((key, label))
        return options

    def export_table(self):
        context = aq_inner(self.context)
        file_ = StringIO()
        writer = csv.DictWriter(file_, self.active_columns,
                                dialect='excel', delimiter=';')
        first_column = self.active_columns[0]
        first_row = dict([(first_column, self.context.absolute_url())])
        writer.writerow(first_row)
        for row in context.getData():
            writer.writerow(dict([
                        (col, safe_utf8(row[col]))
                        for col
                        in self.active_columns]))
        file_.seek(0)
        self.request.RESPONSE.setHeader(
            'Content-Type', 'text/csv; charset=utf-8')
        # we use all parent-ids (seperated by "_") as filename.
        # the user should be able to find the table later..
        # since we do not have enough charactors on windows, we need to use
        # a special numbering for generating the filename:
        # bookid.1.3.2.tableid.csv
        # for the chapters instead of the IDs the position-in-parent is used
        filename = [
            '%s.csv' % self.context.getId(),
            ]
        obj = aq_parent(aq_inner(self.context))
        filename.insert(0, TableOfContents().number(obj))
        filename = '.'.join(filename)
        # set the request and send the file
        self.request.RESPONSE.setHeader('Content-disposition',
                                        'attachment; filename=%s' % filename)
        return file_.read()

    def import_table(self):
        column = self.request.get('column', None)
        stream = self.request.get('file', None)
        enforce = self.request.get('enforce', False) and True
        if not stream:
            IStatusMessage(self.request).addStatusMessage(
                _(u'You didn\'t choose a file.'),
                type='error')
        if not column:
            IStatusMessage(self.request).addStatusMessage(
                _(u'You didn\'t choose a column.'),
                type='error')
        if not stream or not column:
            return False
        context = aq_inner(self.context)

        # make sure the data imported is utf-8 and the BOM was removed
        data = safe_utf8(stream.read().decode('utf-8-sig'))
        # fix bad excel carriage returns
        data = data.replace('\r\n', '\n').replace('\r', '\n')
        dialect = csv.Sniffer().sniff(data)

        first_row_plain, data = data.split('\n', 1)
        first_row = first_row_plain.strip().split(dialect.delimiter)

        reader = csv.DictReader(StringIO(data),
                                fieldnames=self.active_columns,
                                dialect=dialect)
        rows = list(reader)

        # check the first row (containing the url)
        if not enforce:
            url = first_row[0]
            if url != self.context.absolute_url():
                IStatusMessage(self.request).addStatusMessage(
                    _(u'The file does not seem to belong to this table.'),
                    type='error')
                return False

        # import the data
        data = context.getData()
        for i, row in enumerate(rows):
            # XXX This is very ugly! Perhaps we can also add new feature like
            # add new rows, just modify, or delete all rows and build it new
            if i < int(context.getHeaderRows()):
                # do not update header- or footer-rows
                continue
            try:
                data[i][column] = row[column]
            except IndexError:
                break

        context.setData(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u'table_import_successful', default=u'Successfully imported the column.'),
            type='info')
        return self.request.RESPONSE.redirect('.')
