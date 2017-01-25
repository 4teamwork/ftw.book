from ftw.book.behaviors.toc import IShowInToc
from ftw.book.behaviors.toc import IHideTitleFromTOC
from plone.indexer.decorator import indexer
from zope.interface import Interface


@indexer(Interface)
def show_in_toc(context):
    if not IShowInToc.providedBy(context):
        return False

    if getattr(context, 'show_title', None) == False:
        return False

    if IHideTitleFromTOC.providedBy(context):
        return not IHideTitleFromTOC(context).hide_from_toc
    else:
        return True
