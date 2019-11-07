from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book.tests import FunctionalTestCase


class TestBookInternalHyperlinksLaTeX(FunctionalTestCase):

    def test_book_internal_hyperlinks_have_internal_reference(self):
        self.htmlblock.content = ('Link to {}!'.format(
            self.html_link_to(self.textblock2)))

        self.assertEquals(
            'Link to {}!\n'.format(self.latex_hyperref_to(self.textblock2)),
            self.get_latex_view_for(self.htmlblock).render())

    def test_files_are_not_considered_as_internal_link(self):
        self.htmlblock.content = ('Link to file {}!'.format(
            self.html_link_to(self.lorem_file)))

        self.assertEquals(
            'Link to file {}!\n'.format(self.latex_link_to(self.lorem_file)),
            self.get_latex_view_for(self.htmlblock).render())

    def test_spaces_are_not_escaped(self):
        self.grant('Manager')
        aq_parent(aq_inner(self.textblock2)).manage_renameObject(
            self.textblock2.getId(), 'the textblock')
        self.htmlblock.content = self.html_link_to(self.textblock2)
        self.assertEquals(
            self.latex_hyperref_to(self.textblock2).strip(),
            self.get_latex_view_for(self.htmlblock).render().strip())

    def html_link_to(self, obj):
        return '<a class="internal-link" href="{}">{}</a>'.format(
            obj.absolute_url(), obj.Title())

    def latex_hyperref_to(self, obj):
        convert = self.get_latex_layout(obj).get_converter().convert
        return (r'\hyperref[path:%(path)s]{%(title)s\footnote{'
                r'See page \pageref{path:%(path)s}}}') % {
                    'title': convert(obj.Title()),
                    'path': '/'.join(obj.getPhysicalPath())}

    def latex_link_to(self, obj):
        convert = self.get_latex_layout(self.example_book).get_converter().convert
        return (r'\href{%(url)s}{%(label)s\footnote{\href{%(url)s}'
                r'{\url{%(url_label)s}}}}') % {
                    'label': convert(obj.Title()),
                    'url': obj.absolute_url(),
                    'url_label': obj.absolute_url()}
