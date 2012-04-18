import re
from xml.dom import minidom
from ftw.pdfgenerator.utils import html2xmlentities
from ftw.book.interfaces import ITable
from BeautifulSoup import BeautifulSoup


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
        self.createTableHead()
        self.createTableBody()
        self.createTableFoot()
        # render
        html = self.doc.toxml(encoding='utf8')
        # try to remove xml definition
        pattern = re.compile('^<\?xml .*?\?>')
        try:
            html = pattern.sub('', html)
        except:
            pass
        return html

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

    def get_column_properties(self, columnName):
        """ Return the proberties of all columns in a dict.
        key: columnId
        value: properties
        """
        if '_columnProperties' not in dir(self):
            self._columnProperties = {}
            for i, column in enumerate(self.context.columnProperties):
                self._columnProperties[column['columnId']] = column
        return self._columnProperties[columnName]

    @property
    def column_widths(self):
        """ Return the columnwidths in a dict
        """
        column_widths = {}
        for name in self.active_column_names:
            try:
                column_widths[name] = int(self.get_column_properties(
                    name)['width'])
            except ValueError:
                column_widths[name] = 0
        return column_widths

    def create_node_with_text(
        self, tagName, parentNode, text='', content='',  **kwargs):
        """ Return a node with text inside
        """

        if isinstance(text, str):
            text = text.decode('utf-8')

        node = self.create_node(tagName, parentNode, content, **kwargs)
        node.appendChild(self.doc.createTextNode(text))

        return node

    def create_caption(self):
        """ Create the caption node object if we want to show the title
        """
        if not self.context.getShowTitle():
            pass

        self.create_node_with_text(
            'caption', self.table_node, self.context.Title())

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

    def calculate_column_widths(self):
        """ Calculate the width for the columns.
        The user can define his own widths. We have to validate that and
        calculate not setted widths

        mapping: dict with {'colid', width}
        """

        mapping = self.column_widths
        max_width = 100 # %
        given_width = sum([abs(x) for x in mapping.values()])
        widthless_columns = len(filter(lambda x: x==0, mapping.values()))
        remaining_width = max_width - given_width

        # The user has set the width correctly so we can return the dict
        if remaining_width == 0 and widthless_columns == 0:
            pass

        # If the user has set no width or he made calculation errors
        elif widthless_columns == self.active_columns or \
            remaining_width < widthless_columns:

            mapping = self.set_column_width(
                mapping, (max_width / self.active_columns))

        # The user set the width correctly but not for every row
        elif widthless_columns:
            mapping = self.set_column_width(
                mapping, (remaining_width / widthless_columns), 0)

        # Because rounding-problems its possible that we get a rest. We put this
        # rest on the first element
        mapping[mapping.keys()[0]] += max_width - sum(mapping.values())

        return mapping

    def set_column_width(self, mapping, width, width_condition=False):
        """ Set the column-widths in the mapping
        """
        for key in mapping.keys():
            if width_condition is False or mapping[key] == width_condition:
                mapping[key] = width

        return mapping

    def create_colgroup(self):
        """ Create the colgroup and calculate the correct width
        """
        colgroup = self.create_node('colgroup', self.table_node)

        mapping = self.calculate_column_widths()

        # create colgroup
        for name in self.active_column_names:
            width = mapping[name]
            col = self.create_node('col', colgroup, content=False, **{
                    'width': '%i%%' % width,
            })

        return colgroup

    def clean_and_parse_html(html):
        """ Cleanup the given html and parse it
        """
        html = str(BeautifulSoup(html))
        try:
            doc = minidom.parseString('<data>%s</data>' % html)
        except:
            doc = minidom.parseString('<data>FEHLER</data>')
        return doc
    clean_and_parse_html = staticmethod(clean_and_parse_html)

##########################################################

    def create_node(self, tagName, parentNode, content='', **kwargs):
        node = self.doc.createElement(tagName)
        for k, v in kwargs.items():
            if isinstance(v, str) and not isinstance(v, unicode):
                v = v.decode('utf8')
            node.setAttribute(k, v)
        if content!=False:
            if not content:
                content = ' '
            if isinstance(content, unicode):
                content = content.encode('utf8')
            content = html2xmlentities(content)
            contentDoc = TableGenerator.clean_and_parse_html(content)
            contentNode = contentDoc.getElementsByTagName('data')[0]
            for elm in list(contentNode.childNodes):
                node.appendChild(elm)
        parentNode.appendChild(node)
        return node

    def get_classes_for_column(self, part, colName=None, colNum=None):
        if part not in ['head', 'body', 'foot']:
            raise AttributeError(
                'get_classes_for_column(): part argument must be one ' \
                'of "head", "body", "foot"')
        if not colName and not colNum:
            raise AttributeError(
                'get_classes_for_column() requires either colName or ' \
                'colNum attribute')
        if not colName:
            colName = 'column_%i' % colNum
        col = self.get_column_properties(colName)
        classes = []
        if col['alignment']:
            classes.append(col['alignment'])
        if col['bold']:
            classes.append('bold')
        if col['indent']:
            classes.append(col['indent'])
        # lines layout: see getClassesForRow
        if self.context.borderLayout=='grid':
            if part in ['head', 'body']:
                classes.append('border-bottom')
            if colName != self.active_column_names[-1]:
                # ^^ not last column
                classes.append('border-right')
        if self.context.borderLayout=='vertical':
            if colName != self.active_column_names[-1]:
                # ^^ not last column
                classes.append('border-right')
        return classes

    def getClassesForRow(self, part, rowNum, colName):
        try:
            rowClasses = self.context.data[rowNum]['row_format']
        except:
            rowClasses = ''
        rowClasses = rowClasses.split(' ')
        if colName != self.active_column_names[0]:
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

    def createTableHead(self):
        if self.context.getHeaderRows(as_int=True)==0:
            return None
        thead = self.create_node('thead', self.table_node)
        firstRow = True
        for rowNum, row in enumerate(
            self.context.data[:self.context.getHeaderRows(as_int=True)]):
            tr = self.create_node('tr', thead)
            for colName in self.active_column_names:
                attrs = {}
                if firstRow:
                    attrs['id'] = colName
                classes = self.get_classes_for_column('head', colName=colName)
                classes += self.getClassesForRow('head', rowNum, colName)
                if self.context.headerIsBold:
                    classes.append('bold')

                classes = list(set(classes))
                if len(classes)>0:
                    attrs['class'] = ' '.join(classes)
                attrs['align'] = 'left'
                th = self.create_node('th', tr, content=row[colName], **attrs)
            firstRow = False
        return thead

    def createRow(self, part, parentNode, rowNum, row):
        if part not in ['body', 'foot']:
            raise AttributeError(
                'createRow(): part argument must be one of "body", "foot"')
        tr = self.create_node('tr', parentNode)
        firstColumn = True
        breakAfterFirstColumn = False
        for colName in self.active_column_names:
            content = row[colName]
            attrs = {}
            classes = self.get_classes_for_column(part, colName=colName)
            classes += self.getClassesForRow(part, rowNum, colName)
            # cleanup classes
            if 'noborders' in classes:
                for cls in ['border-bottom', 'border-top', 'noborders']:
                    if cls in classes:
                        classes.remove(cls)
                if len(content)==0:
                    content = '<span class="scriptsize">&nbsp;</span>'
            if part=='foot' and self.context.footerIsBold:
                classes.append('bold')
            if 'scriptsize' in classes:
                if 'bold' in classes:
                    classes.remove('bold')
            if len(classes)>0:
                attrs['class'] = ' '.join(classes)
            if 'fullColspan' in classes:
                # show first cell with colspan, dont show folling cells
                classes.remove('fullColspan')
                attrs['colspan'] = str(len(self.active_column_names))
                breakAfterFirstColumn = True

            classes = list(set(classes))
            if firstColumn and self.context.firstColumnIsHeader:
                # create header cell
                attrs['id'] = 'row%i' % rowNum
                attrs['class'] = ' '.join(classes)
                th = self.create_node('th', tr, content=content, **attrs)
            else:
                # create normal cell
                if self.context.firstColumnIsHeader:
                    attrs['headers'] = '%s row%i' % (colName, rowNum)
                else:
                    attrs['headers'] = colName
                td = self.create_node('td', tr, content=content, **attrs)
            firstColumn = False
            if breakAfterFirstColumn:
                break
        return tr

    def createTableBody(self):
        if self.context.getHeaderRows(
            as_int=True) + self.context.getFooterRows(
                as_int=True) >= len(self.context.data):
            # no body rows
            return None
        tbody = self.create_node('tbody', self.table_node)
        bodyRows = self.context.data[self.context.getHeaderRows(
            as_int=True):len(self.context.data)-self.context.getFooterRows(
                as_int=True)]
        for rowNum, row in [(i, bodyRows[i]) for i in range(len(bodyRows))]:
            self.createRow(
                'body', tbody, rowNum+self.context.getHeaderRows(
                as_int=True), row)
        return tbody

    def createTableFoot(self):
        if self.context.getFooterRows(as_int=True)==0:
            return None
        tfoot = self.create_node('tfoot', self.table_node)
        rows = self.context.data[-self.context.getFooterRows(as_int=True):]
        for rowNum in range(len(rows)):
            row = rows[rowNum]
            self.createRow(
                'foot', tfoot, rowNum+len(
                    self.context.data)-self.context.getFooterRows(
                        as_int=True), row)
        return tfoot

