from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.Archetypes import atapi
from ftw.book import _
from ftw.book.config import PROJECTNAME
from ftw.book.interfaces import IBook
from zope.interface import implements


BookSchema = (folder.ATFolderSchema.copy() + \
                  NextPreviousAwareSchema.copy() + \
                  atapi.Schema((

            atapi.BooleanField(
                name='use_titlepage',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_titlepage',
                            default=u'Show table of contents'),
                    description=_(u'book_help_use_titlepage',
                                  default=u''))),

            atapi.BooleanField(
                name='use_toc',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_toc',
                            default=u'Show index'),
                    description=_(u'book_help_use_toc',
                                  default=u''))),

            atapi.BooleanField(
                name='use_lot',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_lot',
                            default=u'Show list of tables'),
                    description=_(u'book_help_use_lot',
                                  default=u''))),

            atapi.BooleanField(
                name='use_loi',
                default=True,
                storage=atapi.AnnotationStorage(),

                widget=atapi.BooleanWidget(
                    label=_(u'book_label_use_loi',
                            default=u'Show list of illustrations'),
                    description=_(u'book_help_use_loi',
                                  default=u''))),


            atapi.StringField(
                name='pagestyle',
                default='oneside',
                storage=atapi.AnnotationStorage(),
                required=True,

                vocabulary=(
                    ('oneside', _(u'Einseitig', default=u'oneside')),
                    ('twoside', _(u'Zweiseitig', default=u'twoside')),
                    ),

                widget=atapi.SelectionWidget(
                    label=_(u'book_label_pagestyle',
                            default=u'Pagestyle'),
                    description=_(u'book_help_pagestyle',
                                  default=u''))),

            )))


BookSchema['title'].storage = atapi.AnnotationStorage()
BookSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BookSchema, folderish=True, moveDiscussion=False)


class Book(folder.ATFolder):
    """example book"""
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


atapi.registerType(Book, PROJECTNAME)
