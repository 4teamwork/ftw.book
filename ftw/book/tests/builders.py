from ftw.builder import builder_registry
from ftw.builder.archetypes import ArchetypesBuilder
from ftw.pdfgenerator.utils import provide_request_layer


class BookBuilder(ArchetypesBuilder):

    portal_type = 'Book'

    def __init__(self, *args, **kwargs):
        super(BookBuilder, self).__init__(*args, **kwargs)
        self.apply_layer = None

    def with_layout(self, layout_iface):
        dotted_name = '.'.join((layout_iface.__module__,
                                layout_iface.__name__))
        self.having(latex_layout=dotted_name)
        self.apply_layer = layout_iface
        return self

    def after_create(self, obj):
        if self.apply_layer:
            provide_request_layer(obj.REQUEST, self.apply_layer)
        super(BookBuilder, self).after_create(obj)


builder_registry.register('book', BookBuilder)


class ChapterBuilder(ArchetypesBuilder):

    portal_type = 'Chapter'

builder_registry.register('chapter', ChapterBuilder)


class ParagraphBuilder(ArchetypesBuilder):

    portal_type = 'Paragraph'

builder_registry.register('paragraph', ParagraphBuilder)


class TableBuilder(ArchetypesBuilder):

    portal_type = 'Table'

    def __init__(self, *args, **kwargs):
        super(TableBuilder, self).__init__(*args, **kwargs)
        self.table = None

    def with_table(self, table):
        """Fills the table with data represented as list of lists.
        """
        self.table = table
        return self

    def after_create(self, obj):
        self._update_table_data(obj, self.table)
        super(TableBuilder, self).after_create(obj)

    def _update_table_data(self, obj, table):
        if not table:
            return

        column_properties = obj.getColumnProperties()
        for column_index in range(len(table[0])):
            column_properties[column_index]['active'] = True

        data = map(lambda row: dict([('column_%i' % num, value)
                                     for num, value in enumerate(row)]),
                   table)
        obj.setData(data)

builder_registry.register('table', TableBuilder)
