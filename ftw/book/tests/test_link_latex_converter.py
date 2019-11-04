from ftw.book.testing import LATEX_ZCML_LAYER
from ftw.pdfgenerator.interfaces import IHTML2LaTeXConverter
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from Products.ATContentTypes.interfaces.link import IATLink
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class TestLinkLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestLinkLaTeXView, self).setUp()

        layout_obj = self.create_dummy()
        alsoProvides(layout_obj, ILaTeXLayout)
        request = self.create_dummy()
        self.converter = getMultiAdapter((object(), request, layout_obj),
                                         IHTML2LaTeXConverter)

    def test_converter(self):
        request = self.create_dummy()
        context = self.providing_stub([IATLink])

        url = 'http://www.google.ch'
        description = 'a link to google'

        self.expect(context.Title()).result('My link')
        self.expect(context.remoteUrl).result(url)
        self.expect(context.getRawDescription()).result(description)

        layout = self.providing_stub([ILaTeXLayout])
        self.expect(layout.get_converter()).result(self.converter)

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)
        latex = view.render()

        self.assertEqual(
            latex,
            '\n'.join((
                    r'\begin{description}',
                    r'\item[My link ' + \
                        '(\href{%s}{%s})]' % (url, url) + \
                        r'{%s}' % description,
                    r'\end{description}')))
