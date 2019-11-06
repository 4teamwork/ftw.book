from ftw.book import _
from ftw.book.interfaces import IChapter
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.interface import implements
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IChapterSchema(Schema):

    title = TextLine(
        title=_(u'label_title', default=u'Title'),
        required=True,
    )


class Chapter(Container):
    implements(IChapter)

    # Prevent acquisition in exclude_from_nav indexer
    # since when IExcludeFromNavigation is not enabled.
    exclude_from_nav = False
