from ftw.book.interfaces import IBook
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.general import NullZipRepresentation
from StringIO import StringIO
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface


class BookZipRepresentation(NullZipRepresentation):
    implements(IZipRepresentation)
    adapts(IBook, Interface)

    def get_files(self, path_prefix=u"", recursive=True, toplevel=True):
        filename = u'{0}.pdf'.format(self.context.getId())

        assembler = getMultiAdapter((self.context, self.request),
                                    IPDFAssembler)

        yield (u'{0}/{1}'.format(path_prefix, filename),
               StringIO(assembler.build_pdf()))
