from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.Archetypes import atapi
from ftw.book import _
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IBook
from zope.interface import implements
from zope.schema.vocabulary import getVocabularyRegistry


BookSchema = (folder.ATFolderSchema.copy() + \
                  NextPreviousAwareSchema.copy() + \
                  atapi.Schema((

            atapi.StringField(
                name='latex_layout',
                required=True,

                vocabulary_factory='ftw.book.layoutsVocabulary',
                default_method='getDefaultLaTeXLayout',

                widget=atapi.SelectionWidget(
                    label=_(u'book_label_layout',
                            default=u'Layout'),
                    description=_(u'book_help_layout',
                                  default=u''))),

            atapi.BooleanField(
                name='use_titlepage',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_titlepage',
                            default=u'Embedd a title page'),
                    description=_(u'book_help_use_titlepage',
                                  default=u''))),

            atapi.BooleanField(
                name='use_toc',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_toc',
                            default=u'Embedd table of contents'),
                    description=_(u'book_help_use_toc',
                                  default=u''))),

            atapi.BooleanField(
                name='use_lot',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_lot',
                            default=u'Embedd list of tables.'),
                    description=_(u'book_help_use_lot',
                                  default=u''))),

            atapi.BooleanField(
                name='use_loi',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_loi',
                            default=u'Embedd list of illustrations'),
                    description=_(u'book_help_use_loi',
                                  default=u''))),


            atapi.StringField(
                name='pagestyle',
                default='oneside',
                storage=atapi.AnnotationStorage(),
                required=True,

                vocabulary=(
                    ('oneside', _(u'pagestyle_oneside', default=u'Oneside')),
                    ('twoside', _(u'pagestyle_twoside', default=u'Twoside')),
                    ),

                widget=atapi.SelectionWidget(
                    label=_(u'book_label_pagestyle',
                            default=u'Pagestyle'),
                    description=_(u'book_help_pagestyle',
                                  default=u''))),

            atapi.StringField(
                name='release',
                default='',
                required=False,
                widget=atapi.StringWidget(
                    label=_(u'book_label_release', default=u'Release'),
                    description=_(u'book_help_release', default=u''))),

            atapi.StringField(
                name='author',
                default='',
                required=False,
                widget=atapi.StringWidget(
                    label=_(u'book_label_author', default=u'Author'),
                    description=_(u'book_help_author', default=u''))),

            atapi.TextField(
                name='author_address',
                default='',
                required=False,
                default_content_type='text/plain',
                allowable_content_types=('text/plain',),
                default_output_type='text/plain',

                widget=atapi.TextAreaWidget(
                    label=_(u'book_label_author_address',
                            default=u'Author Address'),
                    description=_(u'book_help_author_address',
                                  default=u''))),

            )))


BookSchema['title'].storage = atapi.AnnotationStorage()
BookSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BookSchema, folderish=True, moveDiscussion=False)


class Book(folder.ATFolder):
    implements(IBook)

    meta_type = "Book"
    schema = BookSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    use_titlepage = atapi.ATFieldProperty('use_titlepage')
    use_toc = atapi.ATFieldProperty('use_toc')
    use_lot = atapi.ATFieldProperty('use_lot')
    use_loi = atapi.ATFieldProperty('use_loi')
    pagestyle = atapi.ATFieldProperty('pagestyle')

    def getDefaultLaTeXLayout(self):
        voc = getVocabularyRegistry().get(self, 'ftw.book.layoutsVocabulary')

        if len(voc) > 0:
            return voc.by_value.keys()[0]
        else:
            return None


atapi.registerType(Book, PROJECTNAME)
