from ftw.book.interfaces import IBookFileListingBlock
from ftw.book.latex import utils
from ftw.pdfgenerator.view import MakoLaTeXView
from StringIO import StringIO
from zope.component import adapts
from zope.interface import Interface
import lxml.etree
import lxml.html
import re


# widths are in %
COLUMN_WIDTHS = {'col-modified': 12,
                 'col-Creator': 15,
                 'col-getObjSize': 10}


def parsed_html(func):
    def parser(html):
        html = '<div>%s</div>' % html
        doc = lxml.html.parse(StringIO(html))
        func(doc)
        html = lxml.html.tostring(doc.xpath('//body/div')[0])
        return re.sub(r'^<div>(.*)</div>$', '\g<1>', html, flags=re.DOTALL)
    return parser


@parsed_html
def remove_html_links(doc):
    lxml.etree.strip_tags(doc, 'a')


@parsed_html
def remove_table_summary(doc):
    for table in doc.xpath('//table'):
        if 'summary' in table.attrib:
            del table.attrib['summary']


@parsed_html
def remove_table_caption(doc):
    lxml.etree.strip_tags(doc, 'caption')


@parsed_html
def add_table_column_widths(doc):
    for table in doc.xpath('//table'):
        no_width = []
        remaining_width = 100
        for col in table.xpath('//col'):
            if 'class' in col.attrib and \
                    col.attrib['class'] in COLUMN_WIDTHS:
                width = COLUMN_WIDTHS[col.attrib['class']]
                col.attrib['width'] = '%i%%' % width
                remaining_width -= width
            else:
                no_width.append(col)

        width_per_column = int(remaining_width / len(no_width))
        for col in no_width:
            col.attrib['width'] = '%i%%' % width_per_column


class ListingBlockLaTeXView(MakoLaTeXView):
    adapts(IBookFileListingBlock, Interface, Interface)

    def render(self):
        latex = []

        if self.context.show_title:
            latex.append(utils.get_latex_heading(self.context, self.layout))

        latex.append(self.table_latex())
        return '\n'.join(latex)

    def table_latex(self):
        view = self.context.restrictedTraverse('block_view')
        table_html = view.render_table(ignore_columns=('getContentType',))
        table_html = remove_html_links(table_html)
        table_html = remove_table_summary(table_html)
        table_html = remove_table_caption(table_html)
        table_html = add_table_column_widths(table_html)
        return self.convert(table_html)
