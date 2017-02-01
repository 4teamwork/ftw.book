from ftw.book.tests import FunctionalTestCase
from ftw.simplelayout.interfaces import IBlockConfiguration
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID


class TestTextBlockLaTeXView(FunctionalTestCase):

    def setUp(self):
        super(TestTextBlockLaTeXView, self).setUp()
        self.textblock = self.example_book.restrictedTraverse(
            'historical-background/china/first-things-first')
        self.textblock.show_title = True
        self.textblock.hide_from_toc = False
        IBlockConfiguration(self.textblock).store({
            'scale': 'sl_textblock_large',
            'imagefloat': 'no-float',
        })
        self.maxDiff = None

    def test_standard_rendering(self):
        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
This is \textit{some} text.
            ''')

    def test_no_image(self):
        self.textblock.image = None
        self.assert_textblock_latex(
            r'''
\subsection{First things first}
This is \textit{some} text.
            ''')

    def test_no_text(self):
        self.textblock.text = None
        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
            ''')

    def test_no_image_no_text(self):
        self.textblock.image = None
        self.textblock.text = None
        self.assert_textblock_latex(
            r'''
\subsection{First things first}
            ''')

    def test_no_title(self):
        self.textblock.show_title = False
        self.assert_textblock_latex(
            r'''
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
This is \textit{some} text.
            ''')

    def test_hide_from_tock(self):
        self.textblock.hide_from_toc = True
        self.assert_textblock_latex(
            r'''
\subsection*{First things first}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
This is \textit{some} text.
            ''')

    def test_heading_tag_not_allowed_in_text(self):
        # Within books the book structure (section, subsection, etc) is
        # defined using chapters and block titles. Therefore the
        # text of the block should not contain headings since it would
        # result in inconsistent chapter numberings and other problems.

        self.textblock.image = None
        self.textblock.text = RichTextValue(
            u'<h1>the</h1> <h2>heading</h2> <h3>tags</h3> <h4>will</h4> '
            u'<h5>be</h5> <h5>bold</h5>.')

        self.assert_textblock_latex(
            r'''
\subsection{First things first}
{\bf the} {\bf heading} {\bf tags} {\bf will} {\bf be} {\bf bold}.
            ''')

    def test_image_floated_small_left(self):
        IBlockConfiguration(self.textblock).store({
            'scale': 'sl_textblock_small',
            'imagefloat': 'left',
        })

        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\checkheight{\includegraphics[width=0.35\linewidth]{XBlockUUIDX_image}}
\begin{wrapfigure}{l}{0.25\linewidth}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
\end{wrapfigure}
\hspace{0em}%%
This is \textit{some} text.
            ''')

    def test_image_floated_middle_left(self):
        IBlockConfiguration(self.textblock).store({
            'scale': 'sl_textblock_middle',
            'imagefloat': 'left',
        })

        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\checkheight{\includegraphics[width=0.6\linewidth]{XBlockUUIDX_image}}
\begin{wrapfigure}{l}{0.5\linewidth}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
\end{wrapfigure}
\hspace{0em}%%
This is \textit{some} text.
            ''')

    def test_image_floated_small_right(self):
        IBlockConfiguration(self.textblock).store({
            'scale': 'sl_textblock_small',
            'imagefloat': 'right',
        })

        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\checkheight{\includegraphics[width=0.35\linewidth]{XBlockUUIDX_image}}
\begin{wrapfigure}{r}{0.25\linewidth}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
\end{wrapfigure}
\hspace{0em}%%
This is \textit{some} text.
            ''')

    def test_image_floated_middle_right(self):
        IBlockConfiguration(self.textblock).store({
            'scale': 'sl_textblock_middle',
            'imagefloat': 'right',
        })

        self.assert_textblock_latex(
            r'''
\subsection{First things first}
\checkheight{\includegraphics[width=0.6\linewidth]{XBlockUUIDX_image}}
\begin{wrapfigure}{r}{0.5\linewidth}
\includegraphics[width=\linewidth]{XBlockUUIDX_image}
\end{wrapfigure}
\hspace{0em}%%
This is \textit{some} text.
            ''')

    def assert_textblock_latex(self, expected_latex):
        expected_latex = expected_latex.strip()
        got_latex = self.get_latex_view_for(self.textblock).render().strip()
        got_latex = got_latex.replace(IUUID(self.textblock), 'XBlockUUIDX')
        self.assertMultiLineEqual(expected_latex, got_latex)
