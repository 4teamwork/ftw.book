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
        return self.having(image=NamedBlobImage(
            data=Path(path).bytes(),
            filename=u'test.gif'))

    def with_textfile(self, path):
        return self.with_text(Path(path).bytes())

    def with_text(self, text):
        if not isinstance(text, unicode):
            text = text.decode('utf-8')
        return self.having(text=RichTextValue(text))

    def with_default_content(self):
        self.with_image(asset('image.jpg'))
        return self.with_textfile(asset('lorem.html'))


builder_registry.register('book textblock', TextBlockBuilder)


class HTMLBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.book.HtmlBlock'


builder_registry.register('book htmlblock', HTMLBlockBuilder)


class TableBuilder(DexterityBuilder):
    portal_type = 'ftw.book.Table'

    def with_table(self, table):
        """Fills the table with data represented as list of lists.
        """
        self.table = table
        return self

    def with_dummy_table(self):
        return self.with_table(zip(map(str, range(0, 10, 2)),
                                   map(str, range(1, 10, 2))))

    def after_create(self, obj):
        self._update_table_data(obj)
        super(TableBuilder, self).after_create(obj)

    def _update_table_data(self, obj):
        table = getattr(self, 'table', None)
        if not table:
            return

        active_columns = len(table[0])
        for index, column in enumerate(obj.column_properties):
            column['active'] = index < active_columns

        default_row = {'column_%i' % num: '' for num in range(len(obj.column_properties))}
        data = []
        for row in table:
            row_data = default_row.copy()
            row_data.update({'column_%i' % num: val for num, val in enumerate(row)})
            data.append(row_data)
        obj.data = data


builder_registry.register('table', TableBuilder)


class ListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.book.FileListingBlock'

builder_registry.register('book listingblock', ListingBlockBuilder)
