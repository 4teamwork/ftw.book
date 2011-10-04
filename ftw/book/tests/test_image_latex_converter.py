from ftw.book.latex.image import ImageLatexConverter
from plone.mocktestcase import MockTestCase
from simplelayout.base.interfaces import IBlockConfig
from zope.interface import directlyProvides


class TestLatexConverter(MockTestCase):

    def create_providing_dummy(self, provides, **kwargs):
        dummy = self.create_dummy(**kwargs)
        directlyProvides(dummy, provides)
        return dummy

    def create_mocks(self, image_layout, title,
                                   description, uid):
        image = self.create_dummy(size=1)

        view = self.mocker.mock()
        self.expect(view.addImage(uid='%s_image' % uid, image=image))
        self.expect(view.conditionalRegisterPackage('graphicx'))
        self.expect(view.conditionalRegisterPackage('wrapfig'))
        self.expect(view.convert(title)).result(title)
        self.expect(view.convert(description)).result(description)

        context = self.mocker.proxy(
            self.create_providing_dummy(IBlockConfig), spec=None)
        self.expect(context.getImage()).result(image).count(1, None)
        self.expect(context.image_layout).result(image_layout)
        self.expect(context.UID()).result(uid)
        self.expect(context.Title()).result(title)
        self.expect(context.description).result(description)

        return context, view

    def test_no_latex_with_no_image(self):
        request = self.create_dummy()

        context = self.mocker.proxy(
            self.create_providing_dummy(IBlockConfig), spec=None)
        self.expect(context.getImage()).result(object())
        self.expect(context.image_layout).result('no-image')
        self.expect(context.Title()).result('')
        self.expect(context.description).result('')

        view = self.mocker.mock()
        self.expect(view.convert('')).result('').count(2)

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)
        self.assertEqual(latex, '')

    def test_latex_with_small_layout(self):
        request = self.create_dummy()

        context, view = self.create_mocks(
            'small', 'my title', 'my description', '123')

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)

        self.assertEqual(
            latex,
            '\n'.join([
                    r'\begin{wrapfigure}{l}{0.25\textwidth}',
                    r'\begin{center}',
                    r'\includegraphics[width=0.25\textwidth]{123_image}',
                    r'\end{center}',
                    r'\caption{my title: my description}',
                    r'\end{wrapfigure}']))

    def test_latex_with_middle_layout(self):
        request = self.create_dummy()

        context, view = self.create_mocks(
            'middle', 'the title', 'the description', '3434')

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)

        self.assertEqual(
            latex,
            '\n'.join([
                    r'\begin{wrapfigure}{l}{0.5\textwidth}',
                    r'\begin{center}',
                    r'\includegraphics[width=0.5\textwidth]{3434_image}',
                    r'\end{center}',
                    r'\caption{the title: the description}',
                    r'\end{wrapfigure}']))

    def test_latex_with_full_layout(self):
        request = self.create_dummy()

        context, view = self.create_mocks(
            'full', 'title', 'description', '12full')

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)

        self.assertEqual(
            latex,
            '\n'.join([
                    r'\begin{figure}[htbp]',
                    r'\begin{center}',
                    r'\includegraphics[width=\textwidth]{12full_image}',
                    r'\end{center}',
                    r'\caption{title: description}',
                    r'\end{figure}']))

    def test_latex_with_middle_right_layout(self):
        request = self.create_dummy()

        context, view = self.create_mocks(
            'middle-right', 'title', 'description', '1mr')

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)

        self.assertIn(r'\begin{wrapfigure}{r}{0.5\textwidth}', latex)
        self.assertIn(r'\includegraphics[width=0.5\textwidth]{1mr_image}',
                      latex)

    def test_latex_with_middle_small_layout(self):
        request = self.create_dummy()

        context, view = self.create_mocks(
            'small-right', 'title', 'description', '1sr')

        self.replay()

        converter = ImageLatexConverter(context, request)
        latex = converter(context, view)

        self.assertIn(r'\begin{wrapfigure}{r}{0.25\textwidth}', latex)
        self.assertIn(r'\includegraphics[width=0.25\textwidth]{1sr_image}',
                      latex)
