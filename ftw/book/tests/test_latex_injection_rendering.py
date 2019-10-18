from ftw.book.behaviors.clearpage import IClearpage
from ftw.book.behaviors.codeinjection import ILaTeXCodeInjection
from ftw.book.behaviors.columnlayout import IChangeColumnLayout
from ftw.book.interfaces import ILaTeXInjectionController
from ftw.book.interfaces import NO_PREFERRED_LAYOUT
from ftw.book.interfaces import ONECOLUMN_LAYOUT
from ftw.book.interfaces import TWOCOLUMN_LAYOUT
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.book.tests import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyClass


class TestLatexInjection(FunctionalTestCase):

    def test_injected_with_interface(self):
        ILaTeXCodeInjection(self.textblock3).pre_latex_code = 'INJECTED PRE'
        ILaTeXCodeInjection(self.textblock3).post_latex_code = 'INJECTED POST'

        self.assert_latex_code(self.textblock3, r'''
        \label{path:/plone/the-example-book/introduction/versioning}

        % ---- LaTeX injection (pre_latex_code) at /plone/the-example-book/introduction/versioning
        INJECTED PRE
        % ---- end LaTeX injection (pre_latex_code)
        \section*{Versioning}


        % ---- LaTeX injection (post_latex_code) at /plone/the-example-book/introduction/versioning
        INJECTED POST
        % ---- end LaTeX injection (post_latex_code)
        ''')

    def test_column_layout_injected(self):
        chapter = create(Builder('chapter').titled(u'Chapter')
                         .within(create(Builder('book').titled(u'Book'))))
        create(Builder('book textblock').titled(u'A').within(chapter)
               .having(preferred_column_layout=ONECOLUMN_LAYOUT))
        create(Builder('book textblock').titled(u'B').within(chapter)
               .having(preferred_column_layout=TWOCOLUMN_LAYOUT))
        create(Builder('book textblock').titled(u'C').within(chapter)
               .having(preferred_column_layout=NO_PREFERRED_LAYOUT))
        create(Builder('book textblock').titled(u'D').within(chapter)
               .having(preferred_column_layout=TWOCOLUMN_LAYOUT))
        create(Builder('book textblock').titled(u'E').within(chapter)
               .having(preferred_column_layout=ONECOLUMN_LAYOUT))

        self.assert_latex_code(chapter, r'''
        \label{path:/plone/book/chapter}
        \setcounter{chapter}{0}
        \chapter{Chapter}
        \label{path:/plone/book/chapter/a}
        \section{A}



        \label{path:/plone/book/chapter/b}
        \twocolumn
        \section{B}



        \label{path:/plone/book/chapter/c}
        \section{C}



        \label{path:/plone/book/chapter/d}
        \section{D}



        \label{path:/plone/book/chapter/e}
        \onecolumn
        \section{E}
        ''')

    def test_latex_pre_clearpage_injected(self):
        IClearpage(self.textblock3).pre_latex_clearpage = True
        self.assert_latex_code(self.textblock3, r'''
        \label{path:/plone/the-example-book/introduction/versioning}
        \clearpage
        \section*{Versioning}
        ''')

    def test_latex_post_clearpage_injected(self):
        IClearpage(self.textblock3).post_latex_clearpage = True
        self.assert_latex_code(self.textblock3, r'''
        \label{path:/plone/the-example-book/introduction/versioning}
        \section*{Versioning}


        \clearpage
        ''')

    def test_latex_newpage_injected(self):
        IChangeColumnLayout(self.textblock3).pre_latex_newpage = True
        self.assert_latex_code(self.textblock3, r'''
        \label{path:/plone/the-example-book/introduction/versioning}
        \newpage
        \section*{Versioning}
        ''')

    def test_landscape_mode(self):
        chapter = create(Builder('chapter').titled(u'Chapter')
                         .having(landscape=True)
                         .within(create(Builder('book').titled(u'Book'))))
        create(Builder('book textblock').titled(u'A').within(chapter))
        create(Builder('book textblock').titled(u'B').within(chapter))

        self.assert_latex_code(chapter, r'''
        \label{path:/plone/book/chapter}
        \begin{landscape}
        \setcounter{chapter}{0}
        \chapter{Chapter}
        \label{path:/plone/book/chapter/a}
        \section{A}



        \label{path:/plone/book/chapter/b}
        \section{B}



        \end{landscape}
        ''')


class TestLaTeXInjectionController(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestLaTeXInjectionController, self).setUp()

        context = self.create_dummy()
        self.request = self.create_dummy()
        builder = self.create_dummy()

        self.layout = BaseLayout(context, self.request, builder)

    def test_component_is_registered(self):
        self.replay()
        component = queryMultiAdapter((self.layout, self.request),
                                      ILaTeXInjectionController)

        self.assertNotEquals(component, None)

    def test_component_implements_interface(self):
        self.replay()
        component = getMultiAdapter((self.layout, self.request),
                                    ILaTeXInjectionController)
        verifyClass(ILaTeXInjectionController, type(component))

    def test_layout_columns_defaults_to_onecolumn(self):
        self.replay()
        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(),
                         ONECOLUMN_LAYOUT)

    def test_layout_columns_layout_switching_is_persistent(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(), ONECOLUMN_LAYOUT)
        controller.set_layout(TWOCOLUMN_LAYOUT)
        self.assertEqual(controller.get_current_layout(), TWOCOLUMN_LAYOUT)

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertEqual(controller.get_current_layout(), TWOCOLUMN_LAYOUT)
        controller.set_layout(ONECOLUMN_LAYOUT)
        self.assertEqual(controller.get_current_layout(), ONECOLUMN_LAYOUT)

    def test_layout_returns_latex_code(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)

        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')
        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT), '')

        self.assertEqual(controller.set_layout(TWOCOLUMN_LAYOUT),
                         r'\twocolumn')
        self.assertEqual(controller.set_layout(TWOCOLUMN_LAYOUT), '')
        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')

        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT),
                         r'\onecolumn')
        self.assertEqual(controller.set_layout(ONECOLUMN_LAYOUT), '')
        self.assertEqual(controller.set_layout(NO_PREFERRED_LAYOUT), '')

    def test_landscape_disabled_by_default(self):
        self.replay()
        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertFalse(controller.is_landscape())

    def test_landscape_switching_is_persistent(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertFalse(controller.is_landscape())

        controller.set_landscape(1, True)
        self.assertTrue(controller.is_landscape())

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertTrue(controller.is_landscape())

        controller.close_landscape(1)
        self.assertFalse(controller.is_landscape())

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertFalse(controller.is_landscape())

    def test_landscape_setting_returns_latex_code(self):
        self.replay()

        controller = getMultiAdapter((self.layout, self.request),
                                     ILaTeXInjectionController)
        self.assertFalse(controller.is_landscape())

        self.assertEqual(controller.set_landscape('a', True),
                         r'\begin{landscape}')

        self.assertEqual(controller.set_landscape('b', True), r'')
        self.assertEqual(controller.set_landscape('c', False), r'')
        self.assertEqual(controller.close_landscape('c'), r'')
        self.assertEqual(controller.close_landscape('b'), r'')
        self.assertEqual(controller.close_landscape('a'), r'\end{landscape}')

    def test_landscape_enabling_requires_package(self):
        layout = self.mocker.proxy(self.layout)
        self.expect(layout.use_package('lscape'))
        self.replay()

        controller = getMultiAdapter((layout, self.request),
                                     ILaTeXInjectionController)
        self.assertFalse(controller.is_landscape())
        controller.set_landscape(1, True)
