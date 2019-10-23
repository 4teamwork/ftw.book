from ftw.book.latex.layouts import get_layout_behavior_registration
from ftw.upgrade.migration import InplaceMigrator
from zope.component.hooks import getSite
from zope.dottedname.resolve import resolve
from zope.schema.vocabulary import getVocabularyRegistry

try:

    from ftw.simplelayout.migration import migrate_simplelayout_page_state
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
        )

    def migrate_all_book_types(self):
        for migrator_class in self.migrator_classes:
            migrator = migrator_class()
            map(migrator.migrate_object,
                self.objects(migrator.query(),
                             'Migrate {}'.format(migrator_class.__name__)))


class BookMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(BookMigrator, self).__init__(
            new_portal_type='ftw.book.Book',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields + (
                    'lastModifier',  # XXX fix me: migrate from field to annotations
                    'searchwords',
                    'showinsearch',
                    'subject',
                    'topics',
                    'latex_layout',  # self.set_book_layout migrates this field
                )),
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
                    'lastModifier',  # XXX fix me: migrate from field to annotations
                    'subject',
                    'searchwords',
                    'showinsearch',
                    'description',  # chapters no longer have descriptions
                    'effectiveDate',
                    'excludeFromNav',
                    'expirationDate',
                )),
            additional_steps=(
                (migrate_simplelayout_page_state, )
                + additional_steps),
            **kwargs
        )

    def query(self):
        return {'portal_type': 'Chapter', 'sort_on': 'path'}
