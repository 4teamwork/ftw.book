from ftw.book.latex.utils import get_latex_heading
from ftw.book.latex.utils import get_raw_image_data
from ftw.book.latex.utils import ImageLaTeXGenerator
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from plone.uuid.interfaces import IUUID
from StringIO import StringIO
import hashlib
import os


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


class TestImageLaTeXGenerator(FunctionalTestCase):

    def test_small_left_nonfloating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        latex = ImageLaTeXGenerator(block, layout)(block.image, 'small')
        self.assertEqual(
            r'\includegraphics[width=0.25\linewidth]{XUIDX_image}',
            latex.replace(IUUID(block), 'XUIDX'))
        self.assertEquals('\\usepackage{graphicx}\n', layout.get_packages_latex())
        self.assertItemsEqual(
            ['{}_image.jpg'.format(IUUID(block))],
            os.listdir(layout.get_builder().build_directory))

        image_hash = hashlib.md5()
        image_path = os.path.join(layout.get_builder().build_directory,
                                  '{}_image.jpg'.format(IUUID(block)))
        with open(image_path) as image_fio:
            map(image_hash.update, image_fio)

        self.assertEquals(
            '68fe15240f2065ccd2c645f3554aa649',
            image_hash.hexdigest())

    def test_small_left_nonfloating_caption(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'small', caption='The Caption')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\includegraphics[width=0.25\linewidth]{XUIDX_image}
\begin{center}
\addtocounter{figure}{1}
\addcontentsline{lof}{figure}{\protect\numberline {\thechapter.\arabic{figure}}{\ignorespaces The Caption}}
Figure \thechapter.\arabic{figure}: The Caption
\end{center}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals('\\usepackage{graphicx}\n', layout.get_packages_latex())

    def test_small_left_floating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'small', floatable=True)
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\checkheight{\includegraphics[width=0.35\linewidth]{XUIDX_image}}
\begin{wrapfigure}{l}{0.25\linewidth}
\includegraphics[width=\linewidth]{XUIDX_image}
\end{wrapfigure}
\hspace{0em}%%
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n'
            '\\usepackage{wrapfig}\n'
            '\\usepackage{checkheight}\n',
            layout.get_packages_latex())

        self.assertItemsEqual(
            ['{}_image.jpg'.format(IUUID(block)),
             'checkheight.sty'],
            os.listdir(layout.get_builder().build_directory))

    def test_small_left_floating_caption(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'small', floatable=True,
                          caption='The Caption')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\checkheight{\includegraphics[width=0.35\linewidth]{XUIDX_image}}
\begin{wrapfigure}{l}{0.25\linewidth}
\includegraphics[width=\linewidth]{XUIDX_image}
\caption{The Caption}
\end{wrapfigure}
\hspace{0em}%%
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n'
            '\\usepackage{wrapfig}\n'
            '\\usepackage{checkheight}\n',
            layout.get_packages_latex())

    def test_middle_left_nonfloating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'middle')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
            \includegraphics[width=0.5\linewidth]{XUIDX_image}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_full(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'full')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
            \includegraphics[width=\linewidth]{XUIDX_image}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_fullwidth_does_not_float(self):
        """Using a floating area (wrapfigure) with a 100% width causes the
        following text to be floated over the image.
        Since in this case floating is not possible (the image takes 100%)
        it should switch to non-floating even when called with
        ``floatable=True``.
        """

        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'full', floatable=True,
                          caption='My Image')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\includegraphics[width=\linewidth]{XUIDX_image}
\begin{center}
\addtocounter{figure}{1}
\addcontentsline{lof}{figure}{\protect\numberline {\thechapter.\arabic{figure}}{\ignorespaces My Image}}
Figure \thechapter.\arabic{figure}: My Image
\end{center}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_middle_right_nonfloating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'middle-right')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\begin{flushright}
\includegraphics[width=0.5\linewidth]{XUIDX_image}
\end{flushright}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_middle_right_nonfloating_caption(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'middle-right', floatable=False,
                          caption='The Caption')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\begin{flushright}
\includegraphics[width=0.5\linewidth]{XUIDX_image}
\begin{center}
\addtocounter{figure}{1}
\addcontentsline{lof}{figure}{\protect\numberline {\thechapter.\arabic{figure}}{\ignorespaces The Caption}}
Figure \thechapter.\arabic{figure}: The Caption
\end{center}

\end{flushright}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_middle_right_floating_caption(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'middle-right', floatable=True,
                          caption='The Caption')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\checkheight{\includegraphics[width=0.6\linewidth]{XUIDX_image}}
\begin{wrapfigure}{r}{0.5\linewidth}
\includegraphics[width=\linewidth]{XUIDX_image}
\caption{The Caption}
\end{wrapfigure}
\hspace{0em}%%
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n'
            '\\usepackage{wrapfig}\n'
            '\\usepackage{checkheight}\n',
            layout.get_packages_latex())

    def test_small_right_nonfloating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator(block.image, 'middle-right')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\begin{flushright}
\includegraphics[width=0.5\linewidth]{XUIDX_image}
\end{flushright}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())

    def test_unkown_layout(self):
        # The includegraphics options should never have an empty width
        # option, like [image=], so the default is be 100% when the layout
        # is not recognized.
        # Having a [image=] will make pdflatex hang and this will block the
        # zope thread.

        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        latex = ImageLaTeXGenerator(block, layout)(block.image, 'fritz')
        self.assertEqual(
            r'\includegraphics[width=\linewidth]{XUIDX_image}',
            latex.replace(IUUID(block), 'XUIDX'))

    def test_render_floating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator.render(block.image, '0.24', 'c', floatable=True,
                                 caption='The Caption')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\checkheight{\includegraphics[width=0.34\linewidth]{XUIDX_image}}
\begin{wrapfigure}{c}{0.24\linewidth}
\includegraphics[width=\linewidth]{XUIDX_image}
\caption{The Caption}
\end{wrapfigure}
\hspace{0em}%%
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n'
            '\\usepackage{wrapfig}\n'
            '\\usepackage{checkheight}\n',
            layout.get_packages_latex())

    def test_render_nofloating(self):
        block = self.example_book.introduction.get('management-summary')
        layout = self.get_latex_layout()
        generator = ImageLaTeXGenerator(block, layout)
        latex = generator.render(block.image, '0.47', 'c')
        self.maxDiff = None
        self.assertMultiLineEqual(
            r'''
\begin{center}
\includegraphics[width=0.47\linewidth]{XUIDX_image}
\end{center}
            '''.strip(),
            latex.replace(IUUID(block), 'XUIDX').strip())
        self.assertEquals(
            '\\usepackage{graphicx}\n',
            layout.get_packages_latex())


class TestGetRawImageData(FunctionalTestCase):

    def test_get_raw_image_data(self):
        already_raw = 'Image data'
        self.assertEquals(get_raw_image_data(already_raw),
                          already_raw)

        image = self.create_dummy(data=StringIO('stream data'))
        self.assertEquals(get_raw_image_data(image), 'stream data')

        image2 = self.create_dummy(data='direct data')
        self.assertEquals(get_raw_image_data(image2), 'direct data')
