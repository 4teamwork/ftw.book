from ftw.book.interfaces import IBook
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.archetypes import FolderZipRepresentation
from Products.CMFPlone.utils import safe_unicode
from StringIO import StringIO
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IZipRepresentation)
@adapter(IBook, Interface)
class BookZipRepresentation(FolderZipRepresentation):

    def get_files(self, path_prefix=u"", recursive=True, toplevel=True):
        filename = '{0}.pdf'.format(self.context.getId())

        assembler = getMultiAdapter((self.context, self.request),
                                    IPDFAssembler)

        yield (u'{0}/{1}'.format(safe_unicode(path_prefix),
                                 safe_unicode(filename)),
               StringIO(assembler.build_pdf()))

        folder_contents = super(BookZipRepresentation, self).get_files(
            path_prefix, recursive, toplevel)

        for item in folder_contents:
            yield item
