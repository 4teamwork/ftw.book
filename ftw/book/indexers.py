from ftw.book.toc import TableOfContents
from plone.indexer.decorator import indexer
from zope.interface import Interface


@indexer(Interface)
def show_in_toc(context):
    return TableOfContents().in_toc(context)
