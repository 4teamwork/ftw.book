from Acquisition import aq_inner, aq_parent
from Products.Archetypes import atapi
from Products.Archetypes.public import TextField
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from ftw.book import _
from ftw.book.interfaces import IBook
from ftw.book.interfaces import ILaTeXCodeInjectionEnabled
from zope.component import adapts
from zope.interface import implements


class LaTeXCodeField(ExtensionField, TextField):
    pass


class LaTeXCodeInjectionExtender(object):
    adapts(ILaTeXCodeInjectionEnabled)
    implements(ISchemaExtender)

    fields = []

    fields.append(LaTeXCodeField(
            name='preLatexCode',
            schemata='LaTeX',
            default_content_type='application/x-latex',
            allowable_content_types='application/x-latex',
            write_permission='ftw.book: Modify LaTeX Injection',

            widget=atapi.TextAreaWidget(
                label=_(u'pre_latex_code_label',
                        default=u'LaTeX code above content'),
                description=_(u'pre_latex_code_help',
                              default=u''))))

    fields.append(LaTeXCodeField(
            name='postLatexCode',
            schemata='LaTeX',
            default_content_type='application/x-latex',
            allowable_content_types='application/x-latex',
            write_permission='ftw.book: Modify LaTeX Injection',

            widget=atapi.TextAreaWidget(
                label=_(u'post_latex_code_label',
                        default=u'LaTeX code beneath content'),
                description=_(u'post_latex_code_help',
                              default=u''))))

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if not self._context_is_within_book():
            return []

        return self.fields

    def _context_is_within_book(self):
        obj = self.context

        while obj is not None:
            if IBook.providedBy(obj):
                return True

            elif IPloneSiteRoot.providedBy(obj):
                return False

            else:
                obj = aq_parent(aq_inner(obj))

        return False
