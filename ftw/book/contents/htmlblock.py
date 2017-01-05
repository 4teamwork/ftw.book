from ftw.book.interfaces import IHTMLBlock
from ftw.htmlblock.contents.htmlblock import HtmlBlock
from ftw.htmlblock.contents.htmlblock import IHtmlBlockSchema
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IBookHtmlBlockSchema(IHtmlBlockSchema):
    pass


class BookHtmlBlock(HtmlBlock):
    implements(IHTMLBlock)
