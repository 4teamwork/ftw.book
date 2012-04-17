"""Common configuration constants
"""


PROJECTNAME = 'ftw.book'


ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Book': 'ftw.book: Add Book',
    'Chapter': 'simplelayout.types.common: Add Page',
    'HTMLBlock': 'ftw.book: Add HTML Block',
    'Remark': 'ftw.book: Add Remark',
    'Table': 'ftw.book: Add Table',
    }


# Book LaTeX layout registry. Do not change manually, use
# ftw.book.latex.utils.register_book_layout
BOOK_LAYOUT_REGISTRY = {}
