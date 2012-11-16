from StringIO import StringIO
from ftw.book.interfaces import IBook
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.book.latex.utils import get_latex_heading
from ftw.book.latex.utils import get_raw_image_data
from ftw.pdfgenerator.html2latex.utils import generate_manual_caption
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.testing import MockTestCase
from mocker import ANY
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.app.component.hooks import setSite
from zope.component import getGlobalSiteManager
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import alsoProvides


class TestLatexHeading(MockTestCase):

    def mock_inject_settings(self, mock, **settings):
        schema = self.stub()
        self.expect(mock.Schema()).result(schema).count(0, None)

        for fieldname, value in settings.items():
            self.expect(schema.getField(fieldname).get(mock)).result(value)

        self.expect(schema.getField(ANY)).result(None)

        return schema

    def test_latex_heading_of_primary_chapter(self):
        chapter = self.mocker.mock()
        self.set_parent(chapter, self.stub_interface(IBook))
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')
        self.mock_inject_settings(chapter)

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(
            layout.get_converter().convert('My Chapter')).result(
            'My Chapter')

        self.replay()

        self.assertEquals(get_latex_heading(chapter, layout),
                          '\\chapter{My Chapter}\n')

    def test_hide_from_toc_setting_from_latex_injection(self):
        paragraph = self.stub()
        self.set_parent(paragraph, self.stub_interface(IBook))
        self.expect(paragraph.pretty_title_or_id()).result('My Paragraph')

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(layout.get_converter().convert('My Paragraph')).result(
            'My Paragraph')

        with self.mocker.order():
            self.mock_inject_settings(paragraph, hideFromTOC=True)
            self.mock_inject_settings(paragraph, hideFromTOC=True)
            self.mock_inject_settings(paragraph, hideFromTOC=False)

        self.replay()

        self.assertEquals(get_latex_heading(paragraph, layout),
                          '\\chapter*{My Paragraph}\n')

        # Passed "toc" argument should take precedence
        self.assertEquals(get_latex_heading(paragraph, layout, toc=True),
                          '\\chapter{My Paragraph}\n')

        self.assertEquals(get_latex_heading(paragraph, layout, toc=False),
                          '\\chapter*{My Paragraph}\n')

    def test_latex_heading_of_primary_chapter_without_toc(self):
        chapter = self.mocker.mock()
        self.set_parent(chapter, self.stub_interface(IBook))
        self.expect(chapter.pretty_title_or_id()).result('My Chapter')
        self.mock_inject_settings(chapter)

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(layout.get_converter().convert('My Chapter')
                    ).result('My Chapter')

        self.replay()

        self.assertEquals(get_latex_heading(chapter, layout, toc=False),
                          '\\chapter*{My Chapter}\n')

    def test_latex_heading_of_third_level_chapter(self):
        chapter1 = self.mocker.mock()
        self.set_parent(chapter1, self.stub_interface(IBook))

        chapter2 = self.mocker.mock()
        self.set_parent(chapter2, chapter1)

        chapter3 = self.mocker.mock()
        self.set_parent(chapter3, chapter2)
        self.expect(chapter3.pretty_title_or_id()).result('Sub chapter')
        self.mock_inject_settings(chapter3)

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(layout.get_converter().convert('Sub chapter')
                    ).result('Sub chapter')

        self.replay()

        self.assertEquals(get_latex_heading(chapter3, layout),
                          '\\subsection{Sub chapter}\n')

    def test_latex_heading_with_max_level_exceeded(self):
        book = self.providing_stub([IBook])

        # create 10 objects and use the last one
        obj = None
        previous = book
        for i in range(10):
            obj = self.mocker.mock()
            self.set_parent(obj, previous)
            previous = obj

        self.expect(obj.pretty_title_or_id()).result('the title')
        self.mock_inject_settings(obj)

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(layout.get_converter().convert('the title')
                    ).result('the title')

        self.replay()

        # subparagraph is the "smallest" heading..
        self.assertEquals(get_latex_heading(obj, layout),
                          '\\subparagraph{the title}\n')

    def test_not_within_book(self):
        chapter = self.mocker.mock()
        self.set_parent(chapter, self.stub_interface(INavigationRoot))
        self.expect(chapter.pretty_title_or_id()).result('Any chapter')
        self.mock_inject_settings(chapter)

        layout = self.stub_interface(ILaTeXLayout)
        self.expect(layout.get_converter().convert('Any chapter')
                    ).result('Any chapter')

        self.replay()

        self.assertEquals(get_latex_heading(chapter, layout),
                          '\\section{Any chapter}\n')


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
            r'\includegraphics[width=0.25\textwidth]{XUID_image}')

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
                    r'\includegraphics[width=0.25\textwidth]{XUID_image}',
                    generate_manual_caption('THE CAPTION', 'figure'),
                    )))

    def test_small_left_floating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small', floatable=True)

        self.assertEqual(latex, '\n'.join((
                    r'\begin{wrapfigure}{l}{0.25\textwidth}',
                    r'\includegraphics[width=0.25\textwidth]{XUID_image}',
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
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'small', floatable=True,
                          caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{wrapfigure}{l}{0.25\textwidth}',
                    r'\includegraphics[width=0.25\textwidth]{XUID_image}',
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
            r'\includegraphics[width=0.5\textwidth]{XUID_image}')

    def test_full(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'full')

        self.assertEqual(
            latex,
            r'\includegraphics[width=\textwidth]{XUID_image}')

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
                    r'\includegraphics[width=\textwidth]{XUID_image}',
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
                    r'\includegraphics[width=0.5\textwidth]{XUID_image}',
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
                    r'\includegraphics[width=0.5\textwidth]{XUID_image}',
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
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator(self.image, 'middle-right', floatable=True,
                          caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{wrapfigure}{r}{0.5\textwidth}',
                    r'\includegraphics[width=0.5\textwidth]{XUID_image}',
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
                    r'\includegraphics[width=0.25\textwidth]{XUID_image}',
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
                    r'\includegraphics[width=\textwidth]{XUID_image}',
                    )))

    def test_render_floating(self):
        layout = self.mock_interface(ILaTeXLayout)
        self.expect(layout.use_package('graphicx'))
        self.expect(layout.use_package('wrapfig'))
        self.expect(layout.get_builder().add_file('XUID_image.jpg', ANY))
        self.expect(layout.get_converter().convert('The Caption')).result(
            'THE CAPTION')
        self.replay()

        generator = ImageLaTeXGenerator(self.context, layout)
        latex = generator.render(self.image, '0.56', 'c',
                                 floatable=True,
                                 caption='The Caption')

        self.assertEqual(latex, '\n'.join((
                    r'\begin{wrapfigure}{c}{0.56\textwidth}',
                    r'\includegraphics[width=0.56\textwidth]{XUID_image}',
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
                    r'\includegraphics[width=0.56\textwidth]{XUID_image}',
                    r'\end{center}',
                    )))


class TestGetRawImageData(MockTestCase):

    def test_get_raw_image_data(self):
        already_raw = 'Image data'
        self.assertEquals(get_raw_image_data(already_raw),
                          already_raw)

        image = self.create_dummy(data=StringIO('stream data'))
        self.assertEquals(get_raw_image_data(image), 'stream data')

        image2 = self.create_dummy(data='direct data')
        self.assertEquals(get_raw_image_data(image2), 'direct data')
