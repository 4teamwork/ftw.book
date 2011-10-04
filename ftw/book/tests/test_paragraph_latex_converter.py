from Acquisition import aq_inner, aq_parent
from ftw.book.interfaces import IBook
from ftw.book.latex.paragraph import ParagraphLatexConverter
from plone.mocktestcase import MockTestCase
from simplelayout.base.interfaces import IBlockConfig
from zope.interface import directlyProvides


# from plonegov.pdflatex.browser.converter import LatexCTConverter
# from simplelayout.types.common.interfaces import IParagraph



class TestParagraphLatexConverter(MockTestCase):

    def create_providing_dummy(self, provides, **kwargs):
        dummy = self.create_dummy(**kwargs)
        directlyProvides(dummy, provides)
        return dummy

    def test_getImageLatex_no_latex_with_no_image(self):
        request = self.create_dummy()
        view = self.create_dummy()

        context = self.mocker.mock()
        self.expect(context.getImage()).result(None)

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        self.assertEqual(latex, '')

    def test_getImageLatex_with_layout_noimage(self):
        request = self.create_dummy()
        view = self.create_dummy()

        context = self.mocker.proxy(
            self.create_providing_dummy(IBlockConfig), spec=None)

        self.expect(context.getImage()).result(self.create_dummy(size=1))
        self.expect(context.image_layout).result('no-image')
        self.expect(context.getImageCaption()).result('')

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        self.assertEqual(latex, '')

    def create_getImageLatex_mocks(self, image_layout, caption, uid):
        image = self.create_dummy(size=1)

        view = self.mocker.mock()
        self.expect(view.addImage(uid='%s_image' % uid, image=image))
        self.expect(view.conditionalRegisterPackage('graphicx'))
        self.expect(view.conditionalRegisterPackage('wrapfig'))

        context = self.mocker.proxy(
            self.create_providing_dummy(IBlockConfig), spec=None)
        self.expect(context.getImage()).result(image).count(1, None)
        self.expect(context.image_layout).result(image_layout)
        self.expect(context.getImageCaption()).result(caption)
        self.expect(context.UID()).result(uid)

        return context, view

    def test_getImageLatex_with_layout_small(self):
        request = self.create_dummy()

        context, view = self.create_getImageLatex_mocks(
            'small', 'THE image', '123')

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)

        self.assertEqual(
            latex,
            '\n'.join([
                    r'\begin{wrapfigure}{l}{0.25\textwidth}',
                    r'\begin{center}',
                    r'\includegraphics[width=0.25\textwidth]{123_image}',
                    r'\end{center}',
                    r'\caption{THE image}',
                    r'\end{wrapfigure}']))

    def test_getImageLatex_with_middle_layout(self):
        request = self.create_dummy()

        caption = 'middle image caption'
        context, view = self.create_getImageLatex_mocks(
            'middle', caption, '23442')

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        lines = latex.split()

        self.assertEqual(
            lines[0], r'\begin{wrapfigure}{l}{0.5\textwidth}')
        self.assertIn('23442_image', latex)
        self.assertIn('{%s}' % caption, latex)

    def test_getImageLatex_with_full_layout(self):
        request = self.create_dummy()

        caption = 'full image caption'
        context, view = self.create_getImageLatex_mocks(
            'full', caption, '123ff')

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        lines = latex.split()

        self.assertEqual(
            lines[0], r'\begin{figure}[htbp]')
        self.assertIn('123ff_image', latex)
        self.assertIn('{%s}' % caption, latex)
        self.assertEqual(lines[-1], r'\end{figure}')

    def test_getImageLatex_with_middle_right_layout(self):
        request = self.create_dummy()

        caption = 'middle right image caption'
        uid = 'afdsadsf'
        context, view = self.create_getImageLatex_mocks(
            'middle-right', caption, uid)

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        lines = latex.split()

        self.assertEqual(
            lines[0], r'\begin{wrapfigure}{r}{0.5\textwidth}')
        self.assertIn('%s_image' % uid, latex)
        self.assertIn('{%s}' % caption, latex)

    def test_getImageLatex_with_small_right_layout(self):
        request = self.create_dummy()

        caption = 'small right image caption'
        uid = '23442234'
        context, view = self.create_getImageLatex_mocks(
            'small-right', caption, uid)

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getImageLatex(context, view)
        lines = latex.split()

        self.assertEqual(
            lines[0], r'\begin{wrapfigure}{r}{0.25\textwidth}')
        self.assertIn('%s_image' % uid, latex)
        self.assertIn('{%s}' % caption, latex)

    def test_getTextLatex_some_text(self):
        request = self.create_dummy()

        view = self.mocker.mock()
        self.expect(view.convert('Hello little world')).result(
            'Hello little world')

        context = self.mocker.mock()
        self.expect(context.getText()).result(
            ' Hello little world\n').count(2)

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getTextLatex(context, view)

        self.assertEqual(latex, 'Hello little world\n')

    def test_getTextLatex_no_text(self):
        request = self.create_dummy()
        view = self.create_dummy()

        context = self.mocker.mock()
        self.expect(context.getText()).result('')

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter.getTextLatex(context, view)

        self.assertEqual(latex, '')

    def test_full_latex_rendering(self):
        request = self.create_dummy()

        context, view = self.create_getImageLatex_mocks(
            'small', 'THE image', '123')

        self.expect(context.getShowTitle()).result(True)
        self.expect(context.pretty_title_or_id()).result('My block')
        self.expect(context.getText()).result(
            'Thats some text.   ').count(2)

        book = self.create_providing_dummy(IBook)
        self.expect(aq_parent(aq_inner(context))).result(book)

        self.expect(view.convert('Thats some text.')).result(
            'Some converted text.')
        self.expect(view.convert('My block')).result(
            'My fancy block title')
        self.expect(view.level).result(1)
        self.expect(view.context).result(context)

        self.replay()

        converter = ParagraphLatexConverter(context, request)
        latex = converter(context, view)

        self.assertIn(r'\chapter{My fancy block title}', latex)
        self.assertIn(r'\end{wrapfigure}', latex)
        imagepart, textpart = latex.split(r'\end{wrapfigure}')

        self.assertIn(r'\includegraphics', imagepart)
        self.assertIn('123_image', imagepart)
        self.assertIn('Some converted text.', textpart)
