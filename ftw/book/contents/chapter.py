from ftw.book.interfaces import IChapter
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.interface import provider
from zope.schema import TextLine


DXMF = MessageFactory('plone.app.dexterity')


@provider(IFormFieldProvider)
class IChapterSchema(Schema):

    title = TextLine(
        title=DXMF(u'label_title', default=u'Title'),
        required=True,
    )


class Chapter(Container):
    implements(IChapter)

    # Prevent acquisition in exclude_from_nav indexer
    # since when IExcludeFromNavigation is not enabled.
    exclude_from_nav = False
