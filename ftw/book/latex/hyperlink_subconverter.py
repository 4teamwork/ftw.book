from ftw.book import _
from ftw.pdfgenerator.html2latex.subconverters import hyperlink
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate


class BookHyperlinkConverter(hyperlink.HyperlinkConverter):

    def latex_link(self, url, label, url_label):
        if url.startswith(self.get_context().absolute_url()):
            return self.latex_anchor(url, label)

        return super(BookHyperlinkConverter, self).latex_link(url, label,
                                                              url_label)

    def latex_anchor(self, url, label):
        context = self.get_context()
        path = url.replace(context.absolute_url(),
                           '/'.join((context.getPhysicalPath())))
        path = path.split('\#', 1)[0]
        path = path.split('?', 1)[0]
        path = path.replace(r'\%20', ' ')
        path = path.rstrip('/')

        return (r'\hyperref[path:%(path)s]{%(label)s'
                r'\footnote{%(page_label)s}}') % {
            'path': path,
            'label': label,
            'page_label': self._page_label('\pageref{path:%s}' % path)}

    def _page_label(self, pageref):
        msg = _(u'latex_page_reference',
                default=u'See page ${pageref}',
                mapping={'pageref': pageref})

        context = self.get_context()
        context_language_method = getattr(context, 'getLanguage', None)
        if context_language_method:
            language_code = context_language_method()

        else:
            ltool = getToolByName(context, 'portal_languages')
            language_code = ltool.getPreferredLanguage()

        return translate(msg, target_language=language_code).encode('utf-8')
