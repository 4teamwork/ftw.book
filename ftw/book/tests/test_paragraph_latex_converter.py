from ftw.book.interfaces import IBook
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.types.common.interfaces import IParagraph
from zope.app.component.hooks import setSite
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import alsoProvides


class TestParagraphLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def get_mocks(self):
        request = self.create_dummy(getPreferredLanguages=lambda: [])
        alsoProvides(request, IWithinBookLayer)
        alsoProvides(request, IUserPreferredLanguages)

        # mock is not yet in replay mode, so we use another layout dummy..
        layout_obj = self.create_dummy(use_package=lambda pkg_name: None)
        alsoProvides(layout_obj, ILaTeXLayout)
        converter = getMultiAdapter((object(), request, layout_obj),
                                    IHTML2LaTeXConverter)

        context = self.providing_stub([IParagraph, IBlockConfig])

        layout = self.providing_mock([ILaTeXLayout])
        self.expect(layout.get_converter()).result(converter).count(0, None)

        return context, request, layout

    def create_image_mocks(self, image_layout, caption, uid,
                           floated=True):
        context, request, layout = self.get_mocks()

        self.site = self.create_dummy(
            REQUEST=request,
            getSiteManager=getSiteManager)
        setSite(self.site)

        image = self.create_dummy(get_size=lambda: 11, data='hello world')
        builder = self.mocker.mock()

        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.add_file('%s_image.jpg' % uid, image.data))

        self.expect(layout.use_package('graphicx'))
        if floated:
            self.expect(layout.use_package('wrapfig'))

        self.expect(context.getImage()).result(image).count(1, None)
        self.expect(context.image_layout).result(image_layout)
        self.expect(context.getImageCaption()).result(caption)
        self.expect(context.UID()).result(uid)

        return context, request, layout

    def test_get_image_latex_no_latex_with_no_image(self):
        request = self.create_dummy()
        layout = self.create_dummy()

        context = self.providing_stub([IParagraph])
        self.expect(context.getImage()).result(None)

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.get_image_latex(True)
        self.assertEqual(latex, '')

    def test_get_image_latex_with_layout_noimage(self):
        request = self.create_dummy()
        layout = self.create_dummy()

        context = self.providing_stub([IParagraph, IBlockConfig])

        self.expect(context.getImage()).result(self.create_dummy(
                get_size=lambda: 1))
        self.expect(context.image_layout).result('no-image')
        self.expect(context.getImageCaption()).result('')

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.get_image_latex(True)
        self.assertEqual(latex, '')

    def test_get_text_latex_some_text(self):
        context, request, layout = self.get_mocks()

        self.expect(context.getText()).result(
            ' Hello little world\n')

        self.replay()
        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.get_text_latex()

        self.assertEqual(latex, 'Hello little world\n')

    def test_get_text_latex_no_text(self):
        context, request, layout = self.get_mocks()

        self.expect(context.getText()).result('')

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.get_text_latex()

        self.assertEqual(latex, '')

    def test_full_latex_rendering(self):
        paragraph, request, layout = self.create_image_mocks(
            'small', 'THE image', '123')

        self.expect(paragraph.getShowTitle()).result(True)
        self.expect(paragraph.pretty_title_or_id()).result(
            'My <b>block</b> title')
        self.expect(paragraph.getText()).result(
            'Thats <b>some</b> text.   ')

        book = self.providing_stub([IBook])
        self.set_parent(paragraph, book)

        self.replay()

        view = getMultiAdapter((paragraph, request, layout), ILaTeXView)
        latex = view.render()

        self.assertIn(r'\chapter{My {\bf block} title}', latex)
        self.assertIn(r'\end{wrapfigure}', latex)
        imagepart, textpart = latex.split(r'\end{wrapfigure}')

        self.assertIn(r'\includegraphics', imagepart)
        self.assertIn('123_image', imagepart)
        self.assertIn(r'Thats {\bf some} text.', textpart)

    def test_heading_converts_to_bold(self):
        # Within books the book structure (section, subsection, etc) is
        # defined using chapters and paragraph titles. Therefore the
        # text of the paragraph should not contain headings since it would
        # result in inconsistent chapter numberings and other problems.

        context, request, layout = self.get_mocks()

        self.expect(context.getText()).result(
            '<h1>the</h1> <h2>heading</h2> <h3>tags</h3> <h4>will</h4> ' + \
                '<h5>be</h5> <h5>bold</h5>.')

        self.replay()
        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.get_text_latex()

        self.assertEqual(
            latex,
            '{\\bf the} {\\bf heading} {\\bf tags} {\\bf will} ' + \
                '{\\bf be} {\\bf bold}.\n')

    def test_full_latex_rendering_not_floatable(self):
        """Using "full" layout should not make a floatable image
        (wrapfigure), even there is also text in the block.
        """
        paragraph, request, layout = self.create_image_mocks(
            'full', 'THE image', '123', floated=False)

        self.expect(paragraph.getShowTitle()).result(False)
        self.expect(paragraph.getText()).result(
            'Text')

        book = self.providing_stub([IBook])
        self.set_parent(paragraph, book)

        self.replay()

        view = getMultiAdapter((paragraph, request, layout), ILaTeXView)
        latex = view.render()

        self.assertNotIn(r'\end{wrapfigure}', latex)
        self.assertIn(r'Text', latex)
        self.assertIn(r'\includegraphics', latex)
