from ftw.book.latex.layouts import get_layout_behavior_registration
from ftw.upgrade.migration import InplaceMigrator
from operator import methodcaller
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.dottedname.resolve import resolve
from zope.schema.vocabulary import getVocabularyRegistry

try:

    from ftw.simplelayout.migration import migrate_simplelayout_page_state
    from ftw.simplelayout.migration import migrate_sl_image_layout
    from ftw.simplelayout.migration import SL_BLOCK_DEFAULT_IGNORED_FIELDS
    from ftw.upgrade.migration import DUBLIN_CORE_IGNORES

except ImportError, IMPORT_ERROR:
    pass
else:
    IMPORT_ERROR = None


class MigrationUpgradeStepMixin(object):

    @property
    def migrator_classes(self):
        return (
            BookMigrator,
            ChapterMigrator,
            BookTextBlockMigrator,
            HTMLBlockMigrator,
        )

    def migrate_all_book_types(self):
        for migrator_class in self.migrator_classes:
            migrator = migrator_class()
            map(migrator.migrate_object,
                self.objects(migrator.query(),
                             'Migrate {}'.format(migrator_class.__name__)))


def migrate_last_modifier(old_object, new_object):
    value = getattr(old_object, 'lastModifier', None)
    if value:
        IAnnotations(new_object)['collective.lastmodifier'] = value


def get_book_paths():
    catalog = getToolByName(getSite(), 'portal_catalog')
    query = {'portal_type': ['ftw.book.Book', 'Book']}
    brains = catalog.unrestrictedSearchResults(query)
    return map(methodcaller('getPath'), brains)


class BookMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(BookMigrator, self).__init__(
            new_portal_type='ftw.book.Book',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields + (
                    'lastModifier',
                    'searchwords',
                    'showinsearch',
                    'subject',
                    'topics',
                    'latex_layout',  # self.set_book_layout migrates this field
                )),
            additional_steps=(
                (migrate_last_modifier, )
                + additional_steps),
            **kwargs
        )
        self.steps_after_clone = (self.set_book_layout,) + self.steps_after_clone

    def query(self):
        return {'portal_type': 'Book'}

    def set_book_layout(self, old_object, new_object):
        # Executed before migrating fields, so that the fields of the
        # book layout behavior appear in the standard field migration.
        mapping = self.book_layout_dottedname_mapping()
        new_object.latex_layout = mapping[old_object.latex_layout]
        # trigger behavior registration / providing interface etc.
        get_layout_behavior_registration(new_object)

        layout_field_mapping = getattr(self.get_layout_module(old_object.latex_layout),
                                       'OLD_NEW_MAPPING', {})
        for old_fieldname, new_fieldname in layout_field_mapping.items():
            self.field_mapping.setdefault(old_fieldname, new_fieldname)

    def book_layout_dottedname_mapping(self):
        if not hasattr(self, '_book_layout_dottedname_mapping'):
            vocabulary = getVocabularyRegistry().get(getSite(), 'ftw.book.layoutsVocabulary')
            mapping = {}
            for term in vocabulary:
                new_dottedname = term.value
                module = self.get_layout_module(new_dottedname)
                old_dottedname = getattr(module, 'OLD_AT_INTERFACE')
                mapping[old_dottedname] = new_dottedname

            self._book_layout_dottedname_mapping = mapping

        return self._book_layout_dottedname_mapping

    def get_layout_module(self, dottedname):
        return resolve('.'.join(dottedname.split('.')[:-1]))

    def get_at_field_values(self, old_object):
        for item in super(BookMigrator, self).get_at_field_values(old_object):
            yield item

        layout_fieldnames = getattr(self.get_layout_module(old_object.latex_layout),
                                    'OLD_FIELDNAMES')
        for fieldname in layout_fieldnames:
            if fieldname in self.ignore_fields:
                continue
            value = getattr(old_object, fieldname)
            value = self.normalize_at_field_value(None, fieldname, value)
            yield fieldname, value


class ChapterMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(ChapterMigrator, self).__init__(
            new_portal_type='ftw.book.Chapter',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields + (
                    'lastModifier',
                    'subject',
                    'searchwords',
                    'showinsearch',
                    'description',  # chapters no longer have descriptions
                    'effectiveDate',
                    'excludeFromNav',
                    'expirationDate',
                )),
            additional_steps=(
                (migrate_simplelayout_page_state,
                 migrate_last_modifier)
                + additional_steps),
            **kwargs
        )

    def query(self):
        return {'portal_type': 'Chapter', 'sort_on': 'path'}


class BookTextBlockMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(BookTextBlockMigrator, self).__init__(
            new_portal_type='ftw.book.TextBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields + (
                    'lastModifier',
                    'description',
                    'teaserSelectLink',
                    'searchwords',
                    'showinsearch',
                    'teaserExternalUrl',
                    'teaserReference',
                )),
            field_mapping={
                'showTitle': 'show_title',
                'imageAltText': 'image_alt_text',
                'imageCaption': 'image_caption',
                'imageClickable': 'open_image_in_overlay'},
            additional_steps=(
                (migrate_sl_image_layout,
                 migrate_last_modifier)
                + additional_steps),
            **kwargs
        )

    def query(self):
        return {'portal_type': 'BookTextBlock'}


class HTMLBlockMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(HTMLBlockMigrator, self).__init__(
            new_portal_type='ftw.book.HtmlBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields
                + (
                    'description',
                    'lastModifier',
                    'searchwords',
                    'showinsearch',
                )),
            field_mapping={
                'showTitle': 'show_title',
                'text': 'content'
            },
            additional_steps=(
                (migrate_last_modifier, )
                + additional_steps),
            **kwargs)

    def query(self):
        return {'portal_type': 'HTMLBlock', 'path': get_book_paths()}