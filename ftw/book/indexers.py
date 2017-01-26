from ftw.book.helpers import BookHelper
from plone.indexer.decorator import indexer
from zope.interface import Interface


@indexer(Interface)
def show_in_toc(context):
    return BookHelper().is_numbered(context)
