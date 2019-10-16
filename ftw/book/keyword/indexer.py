from ftw.book.interfaces import IBookTextBlock
from lxml.cssselect import CSSSelector
from plone.indexer.decorator import indexer
from StringIO import StringIO
import lxml.html


@indexer(IBookTextBlock)
def book_keywords(obj):
    html = getattr(obj, 'text', None) and obj.text.output
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
