from StringIO import StringIO
from ftw.book.interfaces import IBookTextBlock
from lxml.cssselect import CSSSelector
from plone.indexer.decorator import indexer
import lxml.html


@indexer(IBookTextBlock)
def book_keywords(obj):
    html = obj.getText()
    if not html:
        return []

    if isinstance(html, str):
        html = html.decode('utf-8')

    doc = lxml.html.parse(StringIO(html))
    nodes = doc.xpath(CSSSelector('span.keyword').path)

    keywords = []
    for node in nodes:
        if not node.attrib.get('title'):
            continue
        keywords.append(node.attrib['title'].encode('utf-8').strip())

    return keywords
