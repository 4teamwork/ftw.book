from ftw.book.latex.link import LinkLatexConverter
from plone.mocktestcase import MockTestCase


class TestLinkLatexConverter(MockTestCase):

    def test_converter(self):
        request = self.create_dummy()

        url = 'http://www.google.ch/'
        description = 'a link to google'

        context = self.mocker.mock()
        self.expect(context.Title()).result('My link')
        self.expect(context.remoteUrl).result(url).count(2)
        self.expect(context.getRawDescription()).result(description)

        view = self.mocker.mock()
        self.expect(view.convert('My link')).result(
            'my link title')
        self.expect(view.convert(url)).result(url).count(2)
        self.expect(view.convert(description)).result(description)

        self.replay()

        converter = LinkLatexConverter(context, request)
        latex = converter(context, view)

        self.assertEqual(
            latex,
            '\n'.join((
                    r'\begin{description}',
                    r'\item[my link title ' + \
                        '(\href{%s}{%s})]' % (url, url) + \
                        r'{%s}' % description,
                    r'\end{description}')))
