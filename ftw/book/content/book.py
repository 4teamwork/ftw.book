"""Definition of the Book content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import folder 

from ftw.book import bookMessageFactory as _
from ftw.book.interfaces import IBook
from ftw.book.config import PROJECTNAME

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema


BookSchema = folder.ATFolderSchema.copy() + NextPreviousAwareSchema.copy() + atapi.Schema((

    atapi.BooleanField(
	 	name = 'use_toc',
	 	default = True,
	    storage = atapi.AnnotationStorage(),
	 	widget = atapi.BooleanWidget(
	 		label = 'Show table of contents',
		 	label_msgid = 'book_label_use_toc',
		 	description = '',
		 	description_msgid = 'book_help_use_toc',
		 	i18n_domain = 'ftw.book',
	 	),
 	),

	atapi.BooleanField(
	 	name = 'use_index',
	 	default = True,
	    storage = atapi.AnnotationStorage(),
	 	widget = atapi.BooleanWidget(
	 		label = 'Show index',
		 	label_msgid = 'book_label_use_index',
		 	description = '',
		 	description_msgid = 'book_help_use_index',
		 	i18n_domain = 'ftw.book',
	 	),
 	),

	atapi.BooleanField(
	 	name = 'use_lot',
	 	default = True,
	    storage = atapi.AnnotationStorage(),
	 	widget = atapi.BooleanWidget(
	 		label = 'Show list of tables',
		 	label_msgid = 'book_label_use_lot',
		 	description = '',
		 	description_msgid = 'book_help_use_lot',
		 	i18n_domain = 'ftw.book',
	 	),
	),

	atapi.BooleanField(
	 	name = 'use_loi',
	 	default = True,
	    storage = atapi.AnnotationStorage(),
	 	widget = atapi.BooleanWidget(
	 		label = 'Show list of illustrations',
		 	label_msgid = 'book_label_use_loi',
		 	description = '',
		 	description_msgid = 'book_help_use_loi',
		 	i18n_domain = 'ftw.book',
	 	),
	),


    atapi.StringField(
            name = 'pagestyle',
            default = 'oneside',
		    storage = atapi.AnnotationStorage(),
            vocabulary = (
                    ('oneside', _(u'Einseitig',default=u'oneside')),
                    ('twoside', _(u'Zweiseitig',default=u'twoside')),
            ),
            required = True,
            widget = atapi.SelectionWidget(
                    label = 'Pagestyle',
                    label_msgid = 'book_label_pagestyle',
                    description = '',
                    description_msgid = 'book_help_pagestyle',
				 	i18n_domain = 'ftw.book',
            ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

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
    use_toc = atapi.ATFieldProperty('use_toc')
    use_index = atapi.ATFieldProperty('use_index')
    use_lot = atapi.ATFieldProperty('use_lot')
    use_loi = atapi.ATFieldProperty('use_loi')
    pagestyle = atapi.ATFieldProperty('pagestyle')
	
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Book, PROJECTNAME)
