from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from ftw.book import _
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IBook
from zope.interface import implements
from zope.schema.vocabulary import getVocabularyRegistry


BookSchema = (folder.ATFolderSchema.copy() +
              NextPreviousAwareSchema.copy() +
              atapi.Schema((

            atapi.StringField(
                name='latex_layout',
                required=True,

                vocabulary_factory='ftw.book.layoutsVocabulary',
                default_method='getDefaultLaTeXLayout',

                widget=atapi.SelectionWidget(
                    label=_(u'book_label_layout',
                            default=u'Layout'))),

            atapi.BooleanField(
                name='use_titlepage',
                default=True,

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_titlepage',
                            default=u'Embedd a title page'),
                    description=_(u'book_help_use_titlepage',
                                  default=u''))),

            atapi.BooleanField(
                name='use_toc',
                default=True,

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_toc',
                            default=u'Embedd table of contents'),
                    description=_(u'book_help_use_toc',
                                  default=u''))),

            atapi.BooleanField(
                name='use_lot',
                default=True,

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_lot',
                            default=u'Embedd list of tables.'),
                    description=_(u'book_help_use_lot',
                                  default=u''))),

            atapi.BooleanField(
                name='use_loi',
                default=True,

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_loi',
                            default=u'Embedd list of illustrations'),
                    description=_(u'book_help_use_loi',
                                  default=u''))),

            )))


schemata.finalizeATCTSchema(BookSchema, folderish=True, moveDiscussion=False)


class Book(folder.ATFolder):
    implements(IBook)
    security = ClassSecurityInfo()

    meta_type = "Book"
    schema = BookSchema

    def getDefaultLaTeXLayout(self):
        voc = getVocabularyRegistry().get(self, 'ftw.book.layoutsVocabulary')

        if len(voc) > 0:
            return voc.by_value.keys()[0]
        else:
            return None

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False


atapi.registerType(Book, PROJECTNAME)
