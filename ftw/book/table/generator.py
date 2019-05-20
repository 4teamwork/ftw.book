from BeautifulSoup import BeautifulSoup
from ftw.book.table.calculator import ColumnWidthsCalculator
from ftw.book.table.tablepart import TablePartBody
from ftw.book.table.tablepart import TablePartFooter
from ftw.book.table.tablepart import TablePartHeader
from ftw.book.table.utils import cleanup_standalone_html_tags
from ftw.pdfgenerator.utils import encode_htmlentities
from ftw.pdfgenerator.utils import html2xmlentities
from ftw.pdfgenerator.utils import xml2htmlentities
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import re


BORDER_STYLE_MAPPING = {
    'grid': ['raw-table'],
    'invisible': ['invisible'],
    'fancy_listing': ['raw-table'],
}


class TableGenerator(object):

    def __init__(self, context):
        self.context = context
        self.doc = None
        self.table_node = None
        self._activeColumns = None
        self._columnProperties = None

    def render(self):
        if not self.active_columns:
            return ''

        if not self.context.getData():
            return ''

        self.doc = minidom.Document()
        self.table_node = self.create_table_element()
        self.create_caption()
        self.create_colgroup()
        self.create_table_head()
        self.create_table_body()
        self.create_table_footer()
        # render
        html = self.doc.toxml(encoding='utf8')
        # try to remove xml definition
        pattern = re.compile(r'^<\?xml .*?\?>')
        try:
            html = pattern.sub('', html)
        except TypeError:
            pass
        return xml2htmlentities(html)

    def create_table_element(self):
        """ Create the table
        """
        css_classes = ['notListed']

        css_classes += BORDER_STYLE_MAPPING.get(
            self.context.getBorderLayout(), '')

        if self.context.getNoLifting():
            css_classes.append('no-lifting')

        attrs = {
                'class': ' '.join(css_classes),
        }
        return self._create_node('table', self.doc, **attrs)

    def create_caption(self):
        """ Create the caption node object if we want to show the title
        """
        if not self.context.getShowTitle():
            return

        title = self.context.Title()
        if isinstance(title, str):
            title = title.decode('utf-8')

        self._create_node('caption', self.table_node, title)

    def create_colgroup(self):
        """ Create the colgroup and calculate the correct width
        """
        colgroup = self._create_node('colgroup', self.table_node)
        calculator = ColumnWidthsCalculator()

        widths = calculator(self.column_widths)

        # create colgroup
        for i in range(len(self.active_column_names)):
            self._create_node('col', colgroup, content=False, **{
                    'width': '%i%%' % widths[i],
            })

        return colgroup

    def create_table_head(self):
        """ Create the head of the table based on the setted header-rows
        in the headerRows-field
        """
        num_header_rows = self.context.getHeaderRows(as_int=True)
        if num_header_rows == 0:
            return None

        # Table head
        thead = self._create_node('thead', self.table_node)
        rows = self.context.getData()[:num_header_rows]

        tablepart = TablePartHeader(
            rows,
            thead,
            0,
            self.active_column_names,
            self.context.getFirstColumnIsHeader(),
            self.context.getBorderLayout(),
        )

        self._create_rows(tablepart)

        return thead

    def create_table_body(self):
        """ Create the table body rows
        """
        num_header_rows = self.context.getHeaderRows(as_int=True)
        num_footer_rows = self.context.getFooterRows(as_int=True)
        available_rows = len(self.context.getData())
        num_body_rows = available_rows - (num_header_rows + num_footer_rows)

        if num_body_rows <= 0:
            return None

        tbody = self._create_node('tbody', self.table_node)
        body_begins_at = available_rows - (num_body_rows + num_footer_rows)
        rows = self.context.getData()[
            num_header_rows:len(self.context.getData()) - num_footer_rows]

        tablepart = TablePartBody(
            rows,
            tbody,
            body_begins_at,
            self.active_column_names,
            self.context.getFirstColumnIsHeader(),
            self.context.getBorderLayout(),
        )

        self._create_rows(tablepart)

        return tbody

    def create_table_footer(self):
        """ Create the table footer rows
        """
        num_footer_rows = self.context.getFooterRows(as_int=True)
        if num_footer_rows == 0:
            return None

        footer = self._create_node('tfoot', self.table_node)
        footer_begins_at = len(self.context.getData()) - num_footer_rows
        rows = self.context.getData()[-num_footer_rows:]

        tablepart = TablePartFooter(
            rows,
            footer,
            footer_begins_at,
            self.active_column_names,
            self.context.getFirstColumnIsHeader(),
            self.context.getBorderLayout(),
            self.context.getFooterIsBold(),
        )

        self._create_rows(tablepart)

        return footer

    @property
    def active_columns(self):
        """ Return number of active columns as int
        """
        return len(self.active_column_names)

    @property
    def active_column_names(self):
        """ Return the names of all active columns in a list
        """
        if self._activeColumns is None:
            self._activeColumns = [column['columnId'] for column in
                                   self.context.getColumnProperties()
                                   if column['active']]
        return self._activeColumns

    @property
    def column_widths(self):
        """ Return the columnwidths in a list
        """
        column_widths = []
        for name in self.active_column_names:
            column_widths.append(self._get_column_properties(name)['width'])
        return column_widths

    def _get_column_properties(self, columnName):
        """ Return the proberties of all columns in a dict.
        key: columnId
        value: properties
        """
        if self._columnProperties is None:
            self._columnProperties = {}
            for column in self.context.getColumnProperties():
                self._columnProperties[column['columnId']] = column
        return self._columnProperties[columnName]

    def _set_column_width(self, widths, width, width_condition=False):
        """ Set the column-widths in the widths
        """
        for key in widths.keys():
            if width_condition is False or widths[key] == width_condition:
                widths[key] = width

        return widths

    def _clean_and_parse_html(html):
        """ Cleanup the given html and parse it
        """

        html = cleanup_standalone_html_tags(html)

        html = encode_htmlentities(html.decode('utf-8')).encode('utf-8')
        html = str(BeautifulSoup(html))
        html = html2xmlentities(html)

        html = html.replace('&#60;', '<')
        html = html.replace('&#62;', '>')
        html = html.replace('&#34;', '"')

        try:
            doc = minidom.parseString('<data>%s</data>' % html)
        except (UnicodeEncodeError, ExpatError):
            doc = minidom.parseString('<data>FEHLER</data>')
        return doc
    _clean_and_parse_html = staticmethod(_clean_and_parse_html)

    def _create_rows(self, tablepart):
        """ Create rows with the given tablepart object
        """
        for i, row in enumerate(tablepart.rows):
            tablepart.set_row_node(
                self._create_node(tablepart.get_row_type(), tablepart.parent))

            for j, col_name in enumerate(tablepart.column_names):

                tablepart.set_is_first_cell(j == 0 and True or False)

                cell = self._create_cell(
                    row, col_name, i + tablepart.begin_at, tablepart)

                if 'fullColspan' in self._get_css(
                    i + tablepart.begin_at, col_name, tablepart):

                    # Just set the first cell, then we brak
                    cell.setAttribute(
                        'colspan', str(len(tablepart.column_names)))
                    break

    def _create_cell(self, row, col_name, row_num, tablepart):
        """ Create a cell in a row with
        """
        attrs = {}
        attrs['class'] = ' '.join(self._get_css(row_num, col_name, tablepart))

        # Add additional attrs
        attrs.update(tablepart.get_additional_attrs(row_num, col_name))

        return self._create_node(
            tablepart.get_cell_type(),
            tablepart.get_row_node(),
            tablepart.wrap_text_in_attr(row[col_name]),
            **attrs)

    def _get_css(self, row_num, col_name, tablepart):
        """ Return global css and css generated from a tablepart object
        """
        css = []

        # Add available column css classes
        col = self._get_column_properties(col_name)
        if col['alignment']:
            css.append(col['alignment'])
        if col['bold']:
            css.append('bold')
        if col['indent']:
            css.append(col['indent'])

        # Add available row css classes
        row_classes = self.context.getData()[row_num].get(
            'row_format', '').split(' ')

        if self.active_column_names.index(col_name) != 0:
            # indent10 and indet2 should only indent the first column.
            if 'indent10' in row_classes:
                row_classes.remove('indent10')
            if 'indent2' in row_classes:
                row_classes.remove('indent2')

        css += row_classes

        return tablepart.get_css(css, row_num, col_name)

    def _create_node(self, tag_name, parent_node, content='', **kwargs):
        """ Create a new minidom node
        """
        node = self.doc.createElement(tag_name)

        for key, value in kwargs.items():
            if isinstance(value, str):
                value = value.decode('utf8')
            node.setAttribute(key, value)

        if content is not False:
            if not content:
                content = ' '

            if isinstance(content, unicode):
                content = content.encode('utf8')

            content = html2xmlentities(content)
            contentDoc = TableGenerator._clean_and_parse_html(content)
            contentNode = contentDoc.getElementsByTagName('data')[0]

            for elm in list(contentNode.childNodes):
                node.appendChild(elm)

        parent_node.appendChild(node)

        return node
