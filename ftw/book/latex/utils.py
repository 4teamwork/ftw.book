from Acquisition import aq_inner, aq_parent
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from ftw.book.interfaces import IBook
from ftw.pdfgenerator.html2latex.utils import generate_manual_caption
from plone.app.layout.navigation.interfaces import INavigationRoot


HEADING_COMMANDS = [
    'chapter',
    'section',
    'subsection',
    'subsubsection',
    'paragraph',
    'subparagraph',
    ]


IMAGE_LAYOUTS = {
    'no-image': None,

    'small': {
        'width': '0.25',
        'align': 'l'},

    'middle': {
        'width': '0.5',
        'align': 'l'},

    'full': {
        'width': '',
        'align': ''},

    'middle-right': {
        'width': '0.5',
        'align': 'r'},

    'small-right': {
        'width': '0.25',
        'align': 'r'},
    }


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


class ImageLaTeXGenerator(object):
    """Generates LaTeX code for including images. Optimized for simplelayout
    image layoutes.
    """

    def __init__(self, context, layout):
        """Arguments:
        context -- object where the image is stored on (portal_type Image
        for instance).
        layout -- ILaTeXLayout object.
        """
        self.layout = layout
        self.context = context

    def __call__(self, image, image_layout, floatable=False, caption=False):
        """Arguments:
        image -- The image object, containing the image data.
        image_layout -- Simplelayout image style (e.g. "small" or
        "middle-right").
        floatable -- If there is normal text right after the image, it is
        possible to float it with ``floatable=True``.
        caption -- The caption of the image.
        """
        if image_layout == 'no-image':
            return ''

        width_ratio = self._get_width_ration_by_image_layout(image_layout)
        align = self._get_alignment_by_image_layout(image_layout)
        return self.render(image, width_ratio, align, floatable=floatable,
                           caption=caption)

    def render(self, image, width_ratio, alignment, floatable=False,
               caption=False):
        """Arguments:
        image -- The image object, containing the image data.
        width_ratio -- The LaTeX style ratio (compared with \textwidth) of
        the width of the image (e.g. '0.5').
        alignment -- Alignment ('l', 'c' or 'r').
        floatable -- If there is normal text right after the image, it is
        possible to float it with ``floatable=True``.
        caption -- The caption of the image.
        """

        if floatable and width_ratio in (1, ''):
            # 100% is not really floatable
            floatable = False

        width = r'%s\textwidth' % width_ratio
        latex = self._generate_includegraphics_latex(image, width)
        latex = self._extend_latex_with_caption(latex, caption, floatable)

        if floatable:
            latex = self._extend_latex_with_floating(latex, alignment, width)
        else:
            latex = self._extend_latex_with_alignment(latex, alignment)

        return latex

    def _get_width_ration_by_image_layout(self, image_layout):
        if image_layout in IMAGE_LAYOUTS:
            return IMAGE_LAYOUTS[image_layout]['width']
        else:
            return ''

    def _get_alignment_by_image_layout(self, image_layout):
        if image_layout in IMAGE_LAYOUTS:
            return IMAGE_LAYOUTS[image_layout]['align']
        else:
            return 'l'

    def _get_image_filename(self):
        return '%s_image' % self.context.UID()

    def _generate_includegraphics_latex(self, image, width):
        name = self._get_image_filename()

        self.layout.use_package('graphicx')
        self.layout.get_builder().add_file(
            '%s.jpg' % name, get_raw_image_data(image))

        return r'\includegraphics[width=%s]{%s}' % (width, name)

    def _extend_latex_with_caption(self, latex, caption, floatable):
        if not caption:
            return latex

        caption = self.layout.get_converter().convert(caption)
        if floatable:
            return '%s\n\\caption{%s}' % (latex, caption)

        else:
            return '%s\n%s' % (
                latex,
                generate_manual_caption(caption, 'figure'))

    def _extend_latex_with_alignment(self, latex, alignment):
        if alignment == 'c':
            return '\n'.join((
                    r'\begin{center}',
                    latex,
                    r'\end{center}'))

        elif alignment == 'r':
            return '\n'.join((
                    r'\begin{flushright}',
                    latex,
                    r'\end{flushright}'))

        else:
            return latex

    def _extend_latex_with_floating(self, latex, alignment, width):
        self.layout.use_package('wrapfig')
        return '\n'.join((
                r'\begin{wrapfigure}{%s}{%s}' % (alignment, width),
                latex,
                r'\end{wrapfigure}',
                r'\hspace{0em}%%',
                ))
