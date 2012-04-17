
"""
Provides class for generating HTML-Tables with Table-Objects.
"""
import re

from xml.dom import minidom

from ftw.pdfgenerator.utils import html2xmlentities
from ftw.book.interfaces import ITable

from BeautifulSoup import BeautifulSoup

class TableGenerator(object):

    def __init__(self, object):
        if not ITable.providedBy(object):
            raise AttributeError('TableGenerator(object) : object must implement ITable')
        self.context = object

    def render(self):
        if len(self.getActiveColumnNames())==0:
            return ''
        self.doc = minidom.Document()
        self.tableNode = self.createTableElement()
        self.createCaption()
        self.createColgroup()
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

    def getActiveColumnNames(self):
        if '_activeColumns' not in dir(self):
            self._activeColumns = []
            for colNum in range(len(self.context.columnProperties)):
                col = self.context.columnProperties[colNum]
                colName = 'column_%i' % colNum
                if col['active']:
                    self._activeColumns.append(colName)
        return self._activeColumns

    def getColumnProperties(self, columnName):
        if '_columnProperties' not in dir(self):
            self._columnProperties = {}
            for colNum in range(len(self.context.columnProperties)):
                col = self.context.columnProperties[colNum]
                name = 'column_%i' % colNum
                self._columnProperties[name] = col
        return self._columnProperties[columnName]

    def getClassesForColumn(self, part, colName=None, colNum=None):
        if part not in ['head', 'body', 'foot']:
            raise AttributeError('getClassesForColumn(): part argument must be one of "head", "body", "foot"')
        if not colName and not colNum:
            raise AttributeError('getClassesForColumn() requires either colName or colNum attribute')
        if not colName:
            colName = 'column_%i' % colNum
        col = self.getColumnProperties(colName)
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
            if colName != self.getActiveColumnNames()[-1]:
                # ^^ not last column
                classes.append('border-right')
        if self.context.borderLayout=='vertical':
            if colName != self.getActiveColumnNames()[-1]:
                # ^^ not last column
                classes.append('border-right')
        return classes

    def getClassesForRow(self, part, rowNum, colName):
        try:
            rowClasses = self.context.data[rowNum]['row_format']
        except:
            rowClasses = ''
        rowClasses = rowClasses.split(' ')
        if colName != self.getActiveColumnNames()[0]:
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
            lastRowOfHead = rowNum==len(self.context.data[:self.context.getHeaderRows(as_int=True)])-1
            lastRowOfBody = rowNum==len(self.context.data)-self.context.getFooterRows(as_int=True)-1
            if lastRowOfHead or lastRowOfBody:
                rowClasses.append('border-bottom')
        return rowClasses

    def createNode(self, tagName, parentNode, content='', **kwargs):
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
            contentDoc = TableGenerator.cleanAndParseHTML(content)
            contentNode = contentDoc.getElementsByTagName('data')[0]
            for elm in list(contentNode.childNodes):
                node.appendChild(elm)
        parentNode.appendChild(node)
        return node

    def cleanAndParseHTML(html):
        html = str(BeautifulSoup(html))
        try:
            doc = minidom.parseString('<data>%s</data>' % html)
        except:
            doc = minidom.parseString('<data>FEHLER</data>')
        return doc
    cleanAndParseHTML = staticmethod(cleanAndParseHTML)

    def createTableElement(self):
        cssClasses = ['notListed']
        if self.context.borderLayout=='grid' or self.context.borderLayout=='vertical':
            cssClasses.append('border-grid')
        try:
            if self.context.getNoLifting():
                cssClasses.append('no-lifting')
        except AttributeError:
            pass
        attrs = {
                'summary' : getattr(self.context, 'description', 'jajaja'),
                'class' : ' '.join(cssClasses),
        }
        return self.createNode('table', self.doc, **attrs)

    def createColgroup(self):
        colgroup = self.createNode('colgroup', self.tableNode)
        def getWidthOfColumn(name):
            try:
                return int(self.getColumnProperties(name)['width'])
            except:
                return 0
        # calculate widths
        mapping = dict(zip(*(
                self.getActiveColumnNames(),
                [getWidthOfColumn(name) for name in self.getActiveColumnNames()],
        )))
        widthlessColumns = len(filter(lambda x:x==0, mapping.values()))
        if widthlessColumns==len(mapping):
            # use oldschool algo
            widthPerColumn = 10
            if len(mapping)>10:
                widthPerColumn = 100/len(mapping)
            widthLeft = 100 # %
            for c in self.getActiveColumnNames():
                mapping[c] = widthPerColumn
                widthLeft -= widthPerColumn
            if widthLeft>0:
                # first column is biggest one
                width = widthPerColumn + widthLeft
                mapping[self.getActiveColumnNames()[0]] = width
        elif widthlessColumns!=0:
            widthLeft = 100 - sum(mapping.values())
            if widthLeft<1:
                widthLeft = 2 * widthlessColumns
            widthPerColumn = widthLeft / widthlessColumns
            for k, v in mapping.items():
                if v==0:
                    mapping[k] = widthPerColumn
        # cleanup widths: sum must be 100
        if sum(mapping.values())!=100:
            # ensure there are no negatives
            for k, v in mapping.items():
                if v<0:
                    mapping[k] = v * (-1)
            # scale to sum 100
            widthSum = sum(mapping.values())
            factor = 100 / float(widthSum)
            # fix it
            for k, v in mapping.items():
                mapping[k] = int(float(v) * factor)
            # fix rounding problems
            widthSum = sum(mapping.values())
            firstColumnName = self.getActiveColumnNames()[0]
            mapping[firstColumnName] = mapping[firstColumnName] - widthSum + 100
        # create colgroup
        for name in self.getActiveColumnNames():
            width = mapping[name]
            col = self.createNode('col', colgroup, content=False, **{
                    'width' : '%i%%' % width,
            })
        return colgroup

    def createTableHead(self):
        if self.context.getHeaderRows(as_int=True)==0:
            return None
        thead = self.createNode('thead', self.tableNode)
        firstRow = True
        for rowNum, row in enumerate(self.context.data[:self.context.getHeaderRows(as_int=True)]):
            tr = self.createNode('tr', thead)
            for colName in self.getActiveColumnNames():
                attrs = {}
                if firstRow:
                    attrs['id'] = colName
                classes = self.getClassesForColumn('head', colName=colName)
                classes += self.getClassesForRow('head', rowNum, colName)
                if self.context.headerIsBold:
                    classes.append('bold')

                classes = list(set(classes))
                if len(classes)>0:
                    attrs['class'] = ' '.join(classes)
                attrs['align'] = 'left'
                th = self.createNode('th', tr, content=row[colName], **attrs)
            firstRow = False
        return thead

    def createRow(self, part, parentNode, rowNum, row):
        if part not in ['body', 'foot']:
            raise AttributeError('createRow(): part argument must be one of "body", "foot"')
        tr = self.createNode('tr', parentNode)
        firstColumn = True
        breakAfterFirstColumn = False
        for colName in self.getActiveColumnNames():
            content = row[colName]
            attrs = {}
            classes = self.getClassesForColumn(part, colName=colName)
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
            if 'footnotesize' in classes:
                if 'bold' in classes:
                    classes.remove('bold')
            if len(classes)>0:
                attrs['class'] = ' '.join(classes)
            if 'fullColspan' in classes:
                # show first cell with colspan, dont show folling cells
                classes.remove('fullColspan')
                attrs['colspan'] = str(len(self.getActiveColumnNames()))
                breakAfterFirstColumn = True

            classes = list(set(classes))
            if firstColumn and self.context.firstColumnIsHeader:
                # create header cell
                attrs['id'] = 'row%i' % rowNum
                attrs['class'] = ' '.join(classes)
                th = self.createNode('th', tr, content=content, **attrs)
            else:
                # create normal cell
                if self.context.firstColumnIsHeader:
                    attrs['headers'] = '%s row%i' % (colName, rowNum)
                else:
                    attrs['headers'] = colName
                td = self.createNode('td', tr, content=content, **attrs)
            firstColumn = False
            if breakAfterFirstColumn:
                break
        return tr

    def createTableBody(self):
        if self.context.getHeaderRows(as_int=True) + self.context.getFooterRows(as_int=True) >= len(self.context.data):
            # no body rows
            return None
        tbody = self.createNode('tbody', self.tableNode)
        bodyRows = self.context.data[self.context.getHeaderRows(as_int=True):len(self.context.data)-self.context.getFooterRows(as_int=True)]
        for rowNum, row in [(i, bodyRows[i]) for i in range(len(bodyRows))]:
            self.createRow('body', tbody, rowNum+self.context.getHeaderRows(as_int=True), row)
        return tbody

    def createTableFoot(self):
        if self.context.getFooterRows(as_int=True)==0:
            return None
        tfoot = self.createNode('tfoot', self.tableNode)
        rows = self.context.data[-self.context.getFooterRows(as_int=True):]
        for rowNum in range(len(rows)):
            row = rows[rowNum]
            self.createRow('foot', tfoot, rowNum+len(self.context.data)-self.context.getFooterRows(as_int=True), row)
        return tfoot

    def createCaption(self):
        if self.context.getShowTitle():
            caption = self.createNode('caption', self.tableNode)
            textNode = self.doc.createTextNode(self.context.Title().decode('utf8'))
            caption.appendChild(textNode)

