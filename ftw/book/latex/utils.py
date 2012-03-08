from Acquisition import aq_inner, aq_parent
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
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


def get_latex_heading(context, layout, toc=True):
    title = layout.get_converter().convert(context.pretty_title_or_id())

    # level: depth of rendering
    level = -1
    max_level = len(HEADING_COMMANDS) - 1

    obj = context
    while obj and not IBook.providedBy(obj) and level != max_level:
        obj = aq_parent(aq_inner(obj))
        level += 1

        if INavigationRoot.providedBy(obj):
            # cancel, use section
            level = 1
            break

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


def get_raw_image_data(image):
    # XXX use scaling?
    transformer = ATCTImageTransform()
    img = transformer.getImageAsFile(img=image)

    if img is not None:
        return img.read()

    elif isinstance(image.data, str):
        return image.data

    else:
        return image.data.read()
