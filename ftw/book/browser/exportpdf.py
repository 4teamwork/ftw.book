from ftw.book.latex.book_layout import BookLayout
from zope.publisher.browser import BrowserView


class ExportPDFView(BrowserView):

    def __call__(self):
        arguments = {
            'default_book_settings' : False,
            'pre_compiler': pre_compiler,
        }
        as_pdf = self.context.restrictedTraverse(
            '%s/as_pdf' % '/'.join(self.context.getPhysicalPath())
        )
        return as_pdf(**arguments)


def pre_compiler(view, obj):
    layout = BookLayout()
    layout(view, obj)
