from ftw.book.interfaces import IWithinBookLayer
from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.simplelayout.tests import builders as simplelayout_builders
from path import Path
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage


def asset(filename):
    return Path(__file__).parent.joinpath('assets', filename).abspath()


class BookBuilder(DexterityBuilder):
    portal_type = 'ftw.book.Book'

    def __init__(self, *args, **kwargs):
        super(BookBuilder, self).__init__(*args, **kwargs)
        self.apply_layer = None

    def with_layout(self, layout_iface):
        self.having(latex_layout=layout_iface.__identifier__)
        self.apply_layer = layout_iface
        return self

    def after_create(self, obj):
        provide_request_layer(obj.REQUEST, IWithinBookLayer)
        if self.apply_layer:
            provide_request_layer(obj.REQUEST, self.apply_layer)
        super(BookBuilder, self).after_create(obj)

builder_registry.register('book', BookBuilder)


class ChapterBuilder(simplelayout_builders.ContenPageBuilder):
    portal_type = 'ftw.book.Chapter'

builder_registry.register('chapter', ChapterBuilder)


class TextBlockBuilder(simplelayout_builders.TextBlockBuilder):
    portal_type = 'ftw.book.TextBlock'

    def with_image(self, path):
        self.having(image=NamedBlobImage(
            data=Path(path).bytes(),
            filename=u'test.gif'))

    def with_textfile(self, path):
        return self.having(text=RichTextValue(
            Path(path).bytes().decode('utf-8')))

    def with_default_content(self):
        self.with_image(asset('image.jpg'))
        return self.with_textfile(asset('lorem.html'))


builder_registry.register('book textblock', TextBlockBuilder)


# class BookBuilder(ArchetypesBuilder):

#     portal_type = 'Book'

#     def __init__(self, *args, **kwargs):
#         super(BookBuilder, self).__init__(*args, **kwargs)
#         self.apply_layer = None

#     def with_layout(self, layout_iface):
#         dotted_name = '.'.join((layout_iface.__module__,
#                                 layout_iface.__name__))
#         self.having(latex_layout=dotted_name)
#         self.apply_layer = layout_iface
#         return self

#     def after_create(self, obj):
#         provide_request_layer(obj.REQUEST, IWithinBookLayer)
#         if self.apply_layer:
#             provide_request_layer(obj.REQUEST, self.apply_layer)
#         super(BookBuilder, self).after_create(obj)


# builder_registry.register('book', BookBuilder)


# class ChapterBuilder(ArchetypesBuilder):

#     portal_type = 'Chapter'

# builder_registry.register('chapter', ChapterBuilder)


# class TextBlockBuilder(ArchetypesBuilder):

#     portal_type = 'BookTextBlock'

# builder_registry.register('book textblock', TextBlockBuilder)


# class HTMLBlockBuilder(ArchetypesBuilder):

#     portal_type = 'HTMLBlock'

# builder_registry.register('htmlblock', HTMLBlockBuilder)


# class RemarkBuilder(ArchetypesBuilder):

#     portal_type = 'Remark'

# builder_registry.register('remark', RemarkBuilder)


# class ListingBlockBuilder(ArchetypesBuilder):

#     portal_type = 'ListingBlock'

# builder_registry.register('listingblock', ListingBlockBuilder)


# class TableBuilder(ArchetypesBuilder):

#     portal_type = 'Table'

#     def __init__(self, *args, **kwargs):
#         super(TableBuilder, self).__init__(*args, **kwargs)
#         self.table = None

#     def with_table(self, table):
#         """Fills the table with data represented as list of lists.
#         """
#         self.table = table
#         return self

#     def with_dummy_table(self):
#         return self.with_table(zip(map(str, range(0, 10, 2)),
#                                    map(str, range(1, 10, 2))))

#     def after_create(self, obj):
#         self._update_table_data(obj, self.table)
#         super(TableBuilder, self).after_create(obj)

#     def _update_table_data(self, obj, table):
#         if not table:
#             return

#         column_properties = obj.getColumnProperties()
#         for column_index in range(len(table[0])):
#             column_properties[column_index]['active'] = True

#         data = map(lambda row: dict([('column_%i' % num, value)
#                                      for num, value in enumerate(row)]),
#                    table)
#         obj.setData(data)

# builder_registry.register('table', TableBuilder)
