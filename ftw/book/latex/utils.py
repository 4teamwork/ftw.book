from ftw.book.interfaces import IBook
from plone.app.layout.navigation.interfaces import INavigationRoot


HEADING_COMMANDS = [
    'chapter',
    'section',
    'subsection',
    'subsubsection',
    'paragraph',
    'subparagraph',
    ]


def getLatexHeading(context, view, toc=True):
    title = view.convert(context.pretty_title_or_id())

    # level: depth of rendering
    level = view.level

    # rootObject: object, on which as_pdf was run
    rootObject = view.context

    # fix level depending of rootObject type
    bookOject = rootObject
    while not IBook.providedBy(bookOject):
        bookOject = bookOject.aq_inner.aq_parent
        level += 1
        if INavigationRoot.providedBy(bookOject):
            break

    # decrement level with 2 so that book is -1 and chapter is 0
    level -= 2

    # default command is last in HEADING_COMMANDS
    command = HEADING_COMMANDS[-1]
    if level < len(HEADING_COMMANDS):
        command = HEADING_COMMANDS[level]

    # generate latex
    tocmark = ''
    if not toc:
        tocmark = '*'

    latex = '\%s%s{%s}\n' % (
        command,
        tocmark,
        title)

    return latex
