from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.book.interfaces import IAddRemarkLayer


class ExportBookPDFView(ExportPDFView):
    """Add the IAddRemark request layer if the user likes to show remarks in
    the exported pdf
    """

    index = ViewPageTemplateFile('export_pdf.pt')

    def __call__(self):

        if self.request.get('embed_remarks', False):
            provide_request_layer(self.request, IAddRemarkLayer)

        if self.request.get('submitted', False):
            output = self.request.get('output', 'pdf')
            return self.export(output)

        return self.index()
