import re
from xml.dom import minidom
from ftw.pdfgenerator.utils import html2xmlentities
from BeautifulSoup import BeautifulSoup
from ftw.book.table.tablepart import TablePartBody, TablePartFooter


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
        if self.context.borderLayout in ['grid', 'vertical']:
            css_classes.append('border-grid')

        if self.context.getNoLifting():
            css_classes.append('no-lifting')

        attrs = {
                'summary': getattr(self.context, 'description', ''),
                'class': ' '.join(css_classes),
        }
        return self.create_node('table', self.doc, **attrs)

    def create_caption(self):
        """ Create the caption node object if we want to show the title
        """
        if not self.context.getShowTitle():
            return

        self._create_node_with_text(
            'caption', self.table_node, self.context.Title())

    def create_colgroup(self):
        """ Create the colgroup and calculate the correct width
        """
        colgroup = self.create_node('colgroup', self.table_node)

        widths = self._calculate_column_widths()

        # create colgroup
        for name in self.active_column_names:
            self.create_node('col', colgroup, content=False, **{
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
        thead = self.create_node('thead', self.table_node)

        for i, row in enumerate(self.context.data[:num_header_rows]):

            # Table row
            tr = self.create_node('tr', thead)
            for col_name in self.active_column_names:
                attrs = {}
                attrs['align'] = 'left'
                attrs['class'] = ' '.join(
                    self._get_table_head_css_classes(col_name, i))

                # Table column
                self.create_node('th', tr, content=row[col_name], **attrs)

        return thead

    def create_table_body(self):
        """ Create the table body rows
        """
        num_header_rows = self.context.getHeaderRows(as_int=True)
        num_footer_rows = self.context.getFooterRows(as_int=True)
        available_rows = len(self.context.data)
        num_body_rows = available_rows - (num_header_rows + num_footer_rows)

        if num_body_rows <= 0:
            return None

        tbody = self.create_node('tbody', self.table_node)
        body_begins_at = available_rows - (num_body_rows + num_footer_rows)
        rows = self.context.data[
            num_header_rows:len(self.context.data) - num_footer_rows]

        tablepart = TablePartBody(
            rows,
            tbody,
            body_begins_at,
            self.active_column_names,
            self.context.getFirstColumnIsHeader(),
        )

        self._create_rows(tablepart)

        return tbody

    def create_table_footer(self):
        """ Create the table footer rows
        """
        num_footer_rows = self.context.getFooterRows(as_int=True)
        if num_footer_rows == 0:
            return None

        footer = self.create_node('tfoot', self.table_node)
        footer_begins_at = len(self.context.data) - num_footer_rows
        rows = self.context.data[-num_footer_rows:]

        tablepart = TablePartFooter(
            rows,
            footer,
            footer_begins_at,
            self.active_column_names,
            self.context.getFirstColumnIsHeader(),
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
                self.context.columnProperties if column['active']]
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
            for i, column in enumerate(self.context.columnProperties):
                self._columnProperties[column['columnId']] = column
        return self._columnProperties[columnName]

    def _create_node_with_text(
        self, tag_name, parent_node, text='', content='', **kwargs):
        """ Return a node with text inside
        """

        if isinstance(text, str):
            text = text.decode('utf-8')

        node = self.create_node(tag_name, parent_node, content, **kwargs)
        node.appendChild(self.doc.createTextNode(text))

        return node

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

    def _get_table_head_css_classes(self, col_name, row_num):
        """ Return the css classes for the header-rows
        """

        classes = self.get_classes_for_column('head', col_name)
        classes += self.get_classes_for_row('head', row_num, col_name)

        if self.context.getBorderLayout()=='grid':
            classes.append('border-bottom')
        elif self.context.borderLayout=='lines':
            classes.append('border-top')

        if self.context.getHeaderIsBold:
            classes.append('bold')

        return self._cleanup_css_classes(classes)

    def _create_rows(self, tablepart):
        """ Create rows with the given tablepart object
        """
        for i, row in enumerate(tablepart.get_rows()):
            tablepart.set_row_node(
                self.create_node('tr', tablepart.get_parent()))
            for j, col_name in enumerate(tablepart.get_column_names()):

                tablepart.set_is_first_cell(j == 0 and True or False)
                tablepart.set_css(self._generate_css_for(
                    tablepart.get_part(), i, col_name))

                cell = self._create_cell(row, col_name, i, tablepart)

                if 'fullColspan' in tablepart.get_css():
                    # Just set the first cell, the we brak
                    cell.setAttribute(
                        'colspan', str(len(tablepart.get_column_names())))
                    break

    def _generate_css_for(self, part, row_num, col_name):
        """ Generates the css
        """
        css = self.get_classes_for_column(part, col_name)
        css += self.get_classes_for_row(part, row_num, col_name)
        css = self._cleanup_css_classes(css)

        return css

    def _create_cell(self, row, col_name, row_num, tablepart):
        """ Create a cell in a row with
        """
        attrs = {}
        attrs['class'] = ' '.join(tablepart.get_css())

        if tablepart.is_cell_header_cell():
            # Header cell
            attrs['id'] = 'row%i' % row_num
        elif tablepart.is_first_column_a_header():
            # Normal cell in a row with row headers
            attrs['headers'] = '%s row%i' % (
                col_name, row_num+tablepart.begin_at)
        else:
            # Normal cell
            attrs['headers'] = col_name

        return self.create_node(
            tablepart.get_cell_type(),
            tablepart.get_row_node(),
            row[col_name],
            **attrs)

    def _cleanup_css_classes(self, classes):
        """ Cleanup the css classes used for rows
        """
        if 'noborders' in classes:
            for css_class in ['border-bottom', 'border-top', 'noborders']:
                if css_class in classes:
                    classes.remove(css_class)

        if 'scriptsize' in classes:
            if 'bold' in classes:
                classes.remove('bold')

        return set(classes)

##########################################################
#  Code below is not refactored yet
##########################################################
    def create_node(self, tag_name, parent_node, content='', **kwargs):
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

    def get_classes_for_column(self, part, col_name):
        if part not in ['head', 'body', 'foot']:
            raise AttributeError(
                'get_classes_for_column(): part argument must be one ' \
                'of "head", "body", "foot"')
        col = self._get_column_properties(col_name)
        classes = []
        if col['alignment']:
            classes.append(col['alignment'])
        if col['bold']:
            classes.append('bold')
        if col['indent']:
            classes.append(col['indent'])
        # lines layout: see get_classes_for_row
        if self.context.borderLayout=='grid':
            if part in ['head', 'body']:
                classes.append('border-bottom')
            if col_name != self.active_column_names[-1]:
                # ^^ not last column
                classes.append('border-right')
        if self.context.borderLayout=='vertical':
            if col_name != self.active_column_names[-1]:
                # ^^ not last column
                classes.append('border-right')
        return classes

    def get_classes_for_row(self, part, rowNum, col_name):
        try:
            rowClasses = self.context.data[rowNum]['row_format']
        except:
            rowClasses = ''
        rowClasses = rowClasses.split(' ')

        if part == 'foot' and self.context.getFooterIsBold():
            rowClasses.append('bold')

        if col_name != self.active_column_names[0]:
            # not first column
            if 'indent2' in rowClasses:
                rowClasses.remove('indent2')
            if 'indent10' in rowClasses:
                rowClasses.remove('indent10')
        if self.context.borderLayout=='lines':
            if part=='head' and rowNum==0:
                pass
            elif part=='head':
                rowClasses.append('border-top')
            else:
                rowClasses.append('border-bottom')

        if self.context.borderLayout=='vertical':
            # underline last rows of head and body
            lastRowOfHead = rowNum==len(
                self.context.data[:self.context.getHeaderRows(as_int=True)])-1
            lastRowOfBody = rowNum==len(
                self.context.data)-self.context.getFooterRows(as_int=True)-1
            if lastRowOfHead or lastRowOfBody:
                rowClasses.append('border-bottom')
        return rowClasses
