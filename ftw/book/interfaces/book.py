from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from ftw.book import bookMessageFactory as _

class IBook(Interface):
    """example book"""
    
    # -*- schema definition goes here -*-
