"""Common configuration constants
"""


PROJECTNAME = 'ftw.book'


ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Book': 'ftw.book: Add Book',
    'Chapter': 'ftw.book: Add Chapter',
    'HTMLBlock': 'ftw.book: Add HTML Block',
    'Remark': 'ftw.book: Add Remark',
    'Table': 'ftw.book: Add Table',
    'BookTextBlock': 'ftw.book: Add Book Text Block',
    }


# Book LaTeX layout registry. Do not change manually, use
# ftw.book.latex.utils.register_book_layout
BOOK_LAYOUT_REGISTRY = {}


INDEXES = (('book_keywords', 'KeywordIndex'),
           )
