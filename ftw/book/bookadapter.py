from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book.interfaces import IBook
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IBook)
@adapter(Interface)
def find_book(obj):
    return IBook(aq_parent(aq_inner(obj)))
