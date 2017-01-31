from ftw.book.interfaces import IBook
from ftw.book.latex.utils import get_latex_heading
from ftw.book.latex.utils import get_raw_image_data
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.html2latex.utils import generate_manual_caption
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.testing import MockTestCase
from mocker import ANY
from plone.app.layout.navigation.interfaces import INavigationRoot
from StringIO import StringIO
from unittest2 import skip
from zope.app.component.hooks import setSite
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import alsoProvides


class TestLatexHeading(FunctionalTestCase):

    def test_first_level_chapter(self):
        chapter = self.example_book.get('historical-background')
        self.assertEquals(
            get_latex_heading(chapter, self.get_latex_layout()),
            '\\chapter{Historical Background}\n')
        self.assertEquals(
            get_latex_heading(chapter, self.get_latex_layout(), toc=False),
            '\\chapter*{Historical Background}\n')

    def test_second_level_chapter(self):
        chapter = self.example_book.get('historical-background').china
        self.assertEquals(
            get_latex_heading(chapter, self.get_latex_layout()),
            '\\section{China}\n')

    def test_blocks_hide_from_toc_options(self):
        chapter = self.example_book.get('historical-background').china
        block = chapter.get('first-things-first')
        self.assertEquals(
            get_latex_heading(block, self.get_latex_layout()),
            '\\subsection{First things first}\n')

        block.hide_from_toc = True
        self.assertEquals(
            get_latex_heading(block, self.get_latex_layout()),
            '\\subsection*{First things first}\n')

        self.assertEquals(
            get_latex_heading(block, self.get_latex_layout(), toc=True),
            '\\subsection{First things first}\n')

        block.hide_from_toc = False
        self.assertEquals(
            get_latex_heading(block, self.get_latex_layout(), toc=True),
            '\\subsection{First things first}\n')

        self.assertEquals(
            get_latex_heading(block, self.get_latex_layout(), toc=False),
            '\\subsection*{First things first}\n')

    def test_latex_heading_with_max_level_exceeded(self):
        one = create(Builder('chapter').titled(u'One').within(self.example_book))
        two = create(Builder('chapter').titled(u'Two').within(one))
        three = create(Builder('chapter').titled(u'Three').within(two))
        four = create(Builder('chapter').titled(u'Four').within(three))
        five = create(Builder('chapter').titled(u'Five').within(four))
        six = create(Builder('chapter').titled(u'Six').within(five))
        seven = create(Builder('chapter').titled(u'Seven').within(six))
        eight = create(Builder('chapter').titled(u'Eight').within(seven))

        self.assertEquals(
            ['\\chapter{One}\n',
             '\\section{Two}\n',
             '\\subsection{Three}\n',
             '\\subsubsection{Four}\n',
             '\\paragraph{Five}\n',
             '\\subparagraph{Six}\n',
             '\\subparagraph{Seven}\n',
             '\\subparagraph{Eight}\n'],
            map(lambda obj: get_latex_heading(obj, self.get_latex_layout()),
                (one, two, three, four, five, six, seven, eight)))


@skip('XXX UPDATE ME')
class TestImageLaTeXGenerator(MockTestCase):

    def setUp(self):
        super(TestImageLaTeXGenerator, self).setUp()

        self.image = self.create_dummy(
            get_size=lambda: 11, data='hello world')

        self.context = self.create_dummy(
            UID=lambda: 'XUID')

        setSite(self._create_site_with_request())

    def tearDown(self):
        setSite(None)

    def _create_site_with_request(self):
        request = self.create_dummy(getPreferredLanguages=lambda: [])
        alsoProvides(request, IUserPreferredLanguages)

        site = self.create_dummy(
            REQUEST=request,
            getSiteManager=getGlobalSiteManager)

        return site

    def test_no_image_layout(self):
        self.replay()

        generator = ImageLaTeXGenerator(None, None)
        self.assertEqual(generator(None, 'no-image'), '')

    def test_small_left_nonfloating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small')

        self.assertEqual(
            latex,
            r'\includegraphics[width=0.25\linewidth]{XUID_image}')

    def test_small_left_nonfloating_caption(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small', caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\includegraphics[width=0.25\linewidth]{XUID_image}',
                    generate_manual_caption('THE CAPTION', 'figure'),
                    )))

    def test_small_left_floating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.use_package('checkheight'))
        builder = self.stub()
        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.build_directory).result('/tmp')
        self.expect(builder.add_file('checkheight.sty', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small', floatable=True)

        self.assertEqual(latex, '\n'.join((
                    r'\checkheight{\includegraphics[width=0.35\linewidth]{XUID_image}}',
                    r'\begin{wrapfigure}{l}{0.25\linewidth}',
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    r'\end{wrapfigure}',
                    r'\hspace{0em}%%'
                    )))

    def test_small_left_floating_caption(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.expect(layout.use_package('checkheight'))
        builder = self.stub()
        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.build_directory).result('/tmp')
        self.expect(builder.add_file('checkheight.sty', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small', floatable=True,
                          caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\checkheight{\includegraphics[width=0.35\linewidth]{XUID_image}}',
                    r'\begin{wrapfigure}{l}{0.25\linewidth}',
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    r'\caption{THE CAPTION}',
                    r'\end{wrapfigure}',
                    r'\hspace{0em}%%'
                    )))

    def test_middle_left_nonfloating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'middle')

        self.assertEqual(
            latex,
            r'\includegraphics[width=0.5\linewidth]{XUID_image}')

    def test_full(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'full')

        self.assertEqual(
            latex,
            r'\includegraphics[width=\linewidth]{XUID_image}')

    def test_fullwidth_does_not_float(self):
        """Using a floating area (wrapfigure) with a 100% width causes the
        following text to be floated over the image.
        Since in this case floating is not possible (the image takes 100%)
        it should switch to non-floating even when called with
        ``floatable=True``.
        """

        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('My Image')).result(
            'MY IMAGE')
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'full', floatable=True,
                          caption='My Image')

        self.assertEqual(latex, '\n'.join((
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    generate_manual_caption('MY IMAGE', 'figure'))))

    def test_middle_right_nonfloating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'middle-right')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{flushright}',
                    r'\includegraphics[width=0.5\linewidth]{XUID_image}',
                    r'\end{flushright}',
                    )))

    def test_middle_right_nonfloating_caption(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'middle-right',
                          caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{flushright}',
                    r'\includegraphics[width=0.5\linewidth]{XUID_image}',
                    generate_manual_caption('THE CAPTION', 'figure'),
                    r'\end{flushright}',
                    )))

    def test_middle_right_floating_caption(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.expect(layout.use_package('checkheight'))
        builder = self.stub()
        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.build_directory).result('/tmp')
        self.expect(builder.add_file('checkheight.sty', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'middle-right', floatable=True,
                          caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\checkheight{\includegraphics[width=0.6\linewidth]{XUID_image}}',
                    r'\begin{wrapfigure}{r}{0.5\linewidth}',
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    r'\caption{THE CAPTION}',
                    r'\end{wrapfigure}',
                    r'\hspace{0em}%%'
                    )))

    def test_small_right_nonfloating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small-right')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{flushright}',
                    r'\includegraphics[width=0.25\linewidth]{XUID_image}',
                    r'\end{flushright}',
                    )))

    def test_unkown_layout(self):
        # The includegraphics options should never have an empty width
        # option, like [image=], so the default is be 100% when the layout
        # is not recognized.
        # Having a [image=] will make pdflatex hang and this will block the
        # zope thread.

        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'fancy-unkown')

        self.assertEqual(latex, '\n'.join((
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    )))

    def test_render_floating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.expect(layout.use_package('checkheight'))
        builder = self.stub()
        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.build_directory).result('/tmp')
        self.expect(builder.add_file('checkheight.sty', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator.render(self.image, '0.56', 'c',
                                 floatable=True,
                                 caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\checkheight{\includegraphics[width=0.66\linewidth]{XUID_image}}',
                    r'\begin{wrapfigure}{c}{0.56\linewidth}',
                    r'\includegraphics[width=\linewidth]{XUID_image}',
                    r'\caption{THE CAPTION}',
                    r'\end{wrapfigure}',
                    r'\hspace{0em}%%'
                    )))

    def test_render_nofloating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator.render(self.image, '0.56', 'c')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{center}',
                    r'\includegraphics[width=0.56\linewidth]{XUID_image}',
                    r'\end{center}',
                    )))


@skip('XXX UPDATE ME')
class TestGetRawImageData(MockTestCase):

    def test_get_raw_image_data(self):
        already_raw = 'Image data'
        self.assertEquals(get_raw_image_data(already_raw),
                          already_raw)

        image = self.create_dummy(data=StringIO('stream data'))
        self.assertEquals(get_raw_image_data(image), 'stream data')

        image2 = self.create_dummy(data='direct data')
        self.assertEquals(get_raw_image_data(image2), 'direct data')
