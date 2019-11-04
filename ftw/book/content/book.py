from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from zope.schema.vocabulary import getVocabularyRegistry


BookSchema = (folder.ATFolderSchema.copy() +
              atapi.Schema((

            atapi.IntegerField(
                name='web_toc_depth',
                default=0,
                searchable=False,
                widget=atapi.IntegerWidget()),

            atapi.StringField(
                name='latex_layout',
                required=True,
                vocabulary_factory='ftw.book.layoutsVocabulary',
                default_method='getDefaultLaTeXLayout',
                widget=atapi.SelectionWidget()),

            atapi.BooleanField(
                name='use_titlepage',
                default=True,
                widget=atapi.BooleanWidget()),

            atapi.BooleanField(
                name='use_toc',
                default=True,
                widget=atapi.BooleanWidget()),

            atapi.BooleanField(
                name='use_lot',
                default=True,
                widget=atapi.BooleanWidget()),

            atapi.BooleanField(
                name='use_loi',
                default=True,
                widget=atapi.BooleanWidget()),

            atapi.BooleanField(
                name='use_index',
                default=False,
                widget=atapi.BooleanWidget()))))


schemata.finalizeATCTSchema(BookSchema, folderish=True, moveDiscussion=False)


class Book(folder.ATFolder):
    schema = BookSchema

    def getDefaultLaTeXLayout(self):
        voc = getVocabularyRegistry().get(self, 'ftw.book.layoutsVocabulary')
        if len(voc) > 0:
            return voc.by_value.keys()[0]
        else:
            return None


atapi.registerType(Book, 'ftw.book')
