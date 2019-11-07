from ftw.book import _
from ftw.book.interfaces import IBook
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.component.hooks import getSite
from zope.interface import implements
from zope.interface import provider
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Int
from zope.schema.vocabulary import getVocabularyRegistry


def get_default_LaTeX_layout():
    voc = getVocabularyRegistry().get(getSite(), 'ftw.book.layoutsVocabulary')
    if len(voc) > 0:
        return voc.by_value.keys()[0]
    else:
        return None


@provider(IFormFieldProvider)
class IBookSchema(Schema):

    web_toc_depth = Int(
        title=_(u'label_web_toc_depth', default=u'Table of contents depth'),
        default=0)

    latex_layout = Choice(
        title=_(u'book_label_layout', default=u'Layout'),
        vocabulary=u'ftw.book.layoutsVocabulary',
        defaultFactory=get_default_LaTeX_layout,
        required=True)

    use_titlepage = Bool(
        title=_(u'book_label_use_titlepage', default=u'Embed a title page'),
        default=True)

    use_toc = Bool(
        title=_(u'book_label_use_toc', default=u'Embed table of contents'),
        default=True)

    use_lot = Bool(
        title=_(u'book_label_use_lot', default=u'Embed list of tables'),
        default=True)

    use_loi = Bool(
        title=_(u'book_label_use_loi', default=u'Embed list of illustrations'),
        default=True)

    use_index = Bool(
        title=_(u'book_label_use_index', default=u'Embed subject index'),
        description=_(u'book_help_use_index',
                      default=u'When enabled, a keyword index'
                      u' will be included in the PDF.'),
        default=False)


class Book(Container):
    implements(IBook)

    # Prevent acquisition in exclude_from_nav indexer
    # since when IExcludeFromNavigation is not enabled.
    exclude_from_nav = False

    # XXX Backwards compatiblity methods; should be removed

    def getWeb_toc_depth(self):
        return IBookSchema(self).web_toc_depth

    def getUse_index(self):
        return IBookSchema(self).use_index
