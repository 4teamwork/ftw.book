import csv
from Acquisition import aq_inner, aq_parent
from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ftw.book.helpers import BookHelper
from ftw.book import _


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
        for i, row in enumerate(context.columnProperties):
            if row['active']:
                columns.append('column_%i' % i)
        return columns

    def get_column_options(self):
        context = aq_inner(self.context)
        options = []
        if len(context.data) == 0:
            return options
        options.append(('', ' - Bitte auswaehlen - '))
        first_row = context.data[0].copy()
        for i, row in enumerate(context.columnProperties):
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
        for row in context.data:
            writer.writerow(dict([
                        (col, row[col])
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
            '%s.csv' % self.context.id,
            ]
        obj = aq_parent(aq_inner(self.context))
        filename.insert(0, BookHelper().get_chapter_level_string(obj))
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
        dialect = csv.Sniffer().sniff(stream.readline())
        stream.seek(0)
        reader = csv.DictReader(stream, fieldnames=self.active_columns,
                                dialect=dialect)
        rows = list(reader)
        # check the first row (containing the url)
        if not enforce:
            first_row = rows[0]
            if first_row[
                self.active_columns[0]].strip() != self.context.absolute_url():
                IStatusMessage(self.request).addStatusMessage(
                    _(u'The file does not seem to belong to this table.'),
                    type='error')
                return False

        # import the data
        data = context.getData()
        for i, row in enumerate(rows[1:]):
            # XXX This is very ugly! Perhaps we can also add new feature like
            # add new rows, just modify, or delete all rows and build it new
            if i < context.headerRows:
                # do not update header- or footer-rows
                continue
            try:
                data[i][column] = row[column]
            except IndexError:
                break

        context.setData(data)
        context.processForm()
        message = 'Die Spalte wurde erfolgreich importiert'
        IStatusMessage(self.request).addStatusMessage(message, type='info')
        return self.request.RESPONSE.redirect('.')
