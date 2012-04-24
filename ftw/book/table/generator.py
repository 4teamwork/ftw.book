import re
from xml.dom import minidom
from ftw.pdfgenerator.utils import html2xmlentities
from BeautifulSoup import BeautifulSoup
from ftw.book.table.tablepart import \
    TablePartBody, TablePartFooter, TablePartHeader


class TableGenerator(object):

    def __init__(self, object):
        self.context = object

    def render(self):
        if not self.active_columns:
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
        pattern = re.compile('^<\?xml .*?\?>')
        try:
            html = pattern.sub('', html)
        except:
            pass
        return html

    def create_table_element(self):
        """ Create the table
        """
        css_classes = ['notListed']
        if self.context.getBorderLayout() in ['grid', 'vertical']:
            css_classes.append('border-grid')

        if self.context.getNoLifting():
            css_classes.append('no-lifting')

        attrs = {
                'summary': self.context.Description(),
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

        widths = self._calculate_column_widths()

        # create colgroup
        for name in self.active_column_names:
            self._create_node('col', colgroup, content=False, **{
                    'width': '%i%%' % widths[name],
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
            self.context.getHeaderIsBold(),
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
        if '_activeColumns' not in dir(self):
            self._activeColumns = [column['columnId'] for column in \
                self.context.getColumnProperties() if column['active']]
        return self._activeColumns

    @property
    def column_widths(self):
        """ Return the columnwidths in a dict
        """
        column_widths = {}
        for name in self.active_column_names:
            try:
                column_widths[name] = int(self._get_column_properties(
                    name)['width'])
            except ValueError:
                column_widths[name] = 0
        return column_widths

    def _get_column_properties(self, columnName):
        """ Return the proberties of all columns in a dict.
        key: columnId
        value: properties
        """
        if '_columnProperties' not in dir(self):
            self._columnProperties = {}
            for i, column in enumerate(self.context.getColumnProperties()):
                self._columnProperties[column['columnId']] = column
        return self._columnProperties[columnName]

    def _calculate_column_widths(self):
        """ Calculate the width for the columns.
        The user can define his own widths. We have to validate that and
        calculate not setted widths
        """
        widths = self.column_widths
        max_width = 100 # %
        given_width = sum([abs(x) for x in widths.values()])
        widthless_columns = len(filter(lambda x: x==0, widths.values()))
        remaining_width = max_width - given_width

        # The user has set the width correctly so we can return the dict
        if remaining_width == 0 and widthless_columns == 0:
            pass

        # If the user has set no width or he made calculation errors
        elif widthless_columns == self.active_columns or \
            remaining_width < widthless_columns:

            widths = self._set_column_width(
                widths, (max_width / self.active_columns))

        # The user set the width correctly but not for every row
        elif widthless_columns:
            widths = self._set_column_width(
                widths, (remaining_width / widthless_columns), 0)

        # Because rounding-problems its possible that we get a rest. We add
        # the rest on the first elements width
        widths[widths.keys()[0]] += max_width - sum(widths.values())

        return widths

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
        html = str(BeautifulSoup(html))
        try:
            doc = minidom.parseString('<data>%s</data>' % html)
        except:
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

                cell = self._create_cell(row, col_name, i, tablepart)

                if 'fullColspan' in self._get_css(i, col_name, tablepart):
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
            row[col_name],
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
        css += self.context.getData()[row_num].get('row_format', '').split(' ')

        return tablepart.get_css(css, row_num, col_name)

    def _create_node(self, tag_name, parent_node, content='', **kwargs):
        """ Create a new minidom node
        """
        node = self.doc.createElement(tag_name)

        for key, value in kwargs.items():
            if isinstance(value, str):
                value = value.decode('utf8')
            node.setAttribute(key, value)

        if content != False:
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
