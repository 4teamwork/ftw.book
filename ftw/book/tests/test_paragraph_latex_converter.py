from ftw.book.interfaces import IBook
from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.types.common.interfaces import IParagraph
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class TestParagraphLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def get_mocks(self):
        # mock is not yet in replay mode, so we use another layout dummy..
        layout_obj = self.create_dummy()
        alsoProvides(layout_obj, ILaTeXLayout)
        converter = getMultiAdapter((object(), object(), layout_obj),
                                    IHTML2LaTeXConverter)

        context = self.providing_stub([IParagraph, IBlockConfig])
        request = self.create_dummy()
        layout = self.providing_mock([ILaTeXLayout])
        self.expect(layout.get_converter()).result(converter).count(0, None)

        return context, request, layout

    def create_image_mocks(self, image_layout, caption, uid):
        context, request, layout = self.get_mocks()

        image = self.create_dummy(get_size=lambda: 11, data='hello world')
        builder = self.mocker.mock()

        self.expect(layout.get_builder()).result(builder)
        self.expect(builder.add_file('%s_image.jpg' % uid, image.data))

        self.expect(layout.use_package('graphicx'))
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
