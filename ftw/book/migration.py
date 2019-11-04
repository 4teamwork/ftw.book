from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from copy import deepcopy
from ftw.book.latex.layouts import get_layout_behavior_registration
from ftw.upgrade.migration import InplaceMigrator
from operator import methodcaller
from plone import api
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.dottedname.resolve import resolve
from zope.schema.vocabulary import getVocabularyRegistry
import os

try:

    from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
    from ftw.simplelayout.interfaces import IBlockConfiguration
    from ftw.simplelayout.interfaces import IPageConfiguration
    from ftw.simplelayout.migration import migrate_simplelayout_page_state
    from ftw.simplelayout.migration import SL_BLOCK_DEFAULT_IGNORED_FIELDS
    from ftw.upgrade.migration import DEFAULT_ATTRIBUTES_TO_COPY
    from ftw.upgrade.migration import DUBLIN_CORE_IGNORES
    import ftw.book.content.book  # noqa
    import ftw.book.content.chapter  # noqa
    import ftw.book.content.htmlblock  # noqa
    import ftw.book.content.table  # noqa
    import ftw.book.content.textblock  # noqa

except ImportError, IMPORT_ERROR:
    pass
else:
    IMPORT_ERROR = None


# Tell the upgrade step in ftwbook.graphicblock that the graphicblock
# migration should not be executed, because we need to migrate the chapters
# first and the graphicblock migration will be triggered from here.
os.environ['FTWBOOK_GRAPHICBLOCK_SKIP_DEXTERITY_MIGRATION'] = 'true'


def get_book_paths():
    catalog = getToolByName(getSite(), 'portal_catalog')
    query = {'portal_type': ['ftw.book.Book', 'Book']}
    brains = catalog.unrestrictedSearchResults(query)
    return map(methodcaller('getPath'), brains)


class MigrationUpgradeStepMixin(object):

    @property
    def migrator_classes(self):
        classes = [
            BookMigrator,
            ChapterMigrator,
            TableMigrator,
            BookTextBlockMigrator,
            BookListingBlockMigrator,
            ImageToBookTextBlockMigrator,
            HTMLBlockMigrator,
        ]

        try:
            from ftwbook.graphicblock.migration import GraphicBlockMigrator
        except ImportError:
            pass
        else:
            classes.append(GraphicBlockMigrator)

        return classes

    def migrate_all_book_types(self):
        self.verify()
        for migrator_class in self.migrator_classes:
            migrator = migrator_class()
            query = migrator.query()
            query.setdefault('path', get_book_paths())
            objects = tuple(self.objects(query, 'Migrate {}'.format(migrator_class.__name__)))
            map(migrator.migrate_object, objects)

        self.post_migration_update_page_configs()

    def verify(self):
        brains = self.catalog_unrestricted_search({'portal_type': 'Remark'})
        if len(brains):
            raise ValueError(
                'The new ftw.book version does no longer provide a "Remark" block. '
                'Before migrating to dexterity, all remarks must be removed. '
                'You may want to convert them to textblocks.')

    def post_migration_update_page_configs(self):
        query = {'portal_type': ['ftw.book.Chapter']}
        for obj in self.objects(query, 'Update page configs of chapters'):
            # At this point we have an incomplete page config.
            # We need to reset it and rebuild it from scratch in order to
            # properly include all blocks.
            IPageConfiguration(obj).store({'default': []}, update_positions=False)
            synchronize_page_config_with_blocks(obj)


class BookTypeMigratorBase(InplaceMigrator):

    schemaextender_fields = {
        'preLatexCode': 'pre_latex_code',  # XXX <BaseUnit at a.-gesetzgebung/preLatexCode>
        'postLatexCode': 'post_latex_code',
        'preferredColumnLayout': 'preferred_column_layout',
        'latexLandscape': 'landscape',
        'preLatexClearpage': 'pre_latex_clearpage',
        'postLatexClearpage': 'post_latex_clearpage',
        'preLatexNewpage': 'pre_latex_newpage',
        'hideFromTOC': 'hide_from_toc',
    }

    def __init__(self, *args, **kwargs):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        kwargs.setdefault('attributes_to_migrate',
                          DEFAULT_ATTRIBUTES_TO_COPY + ('creators',))
        if 'field_mapping' in kwargs:
            kwargs['field_mapping'].update(self.schemaextender_fields)
        else:
            kwargs['field_mapping'] = dict(self.schemaextender_fields)
        super(BookTypeMigratorBase, self).__init__(*args, **kwargs)

    def migrate_sl_image_layout(self, old_object, new_object):
        block_layout_mapping = {
            'small': {
                'scale': 'sl_textblock_small',
                'imagefloat': 'left'},
            'middle': {
                'scale': 'sl_textblock_middle',
                'imagefloat': 'left'},
            'full': {
                'scale': 'sl_textblock_large',
                'imagefloat': 'no-float'},
            'middle-right': {
                'scale': 'sl_textblock_middle',
                'imagefloat': 'right'},
            'small-right': {
                'scale': 'sl_textblock_small',
                'imagefloat': 'right'},
            'no-image': {
                'scale': 'sl_textblock_small',
                'imagefloat': 'left'},
        }

        image_layout = IAnnotations(old_object).get('imageLayout', None)
        if not image_layout or image_layout == 'dummy-dummy-dummy':
            return

        new_config = IBlockConfiguration(new_object)
        cfg = new_config.load()
        cfg.update(block_layout_mapping[image_layout])
        new_config.store(cfg)

    def migrate_last_modifier(self, old_object, new_object):
        value = getattr(old_object, 'lastModifier', None)
        if value:
            IAnnotations(new_object)['collective.lastmodifier'] = value

    def get_old_schemaextender_fieldnames(self, old_object):
        return list(self.schemaextender_fields)

    def get_at_field_values(self, old_object):
        for item in super(BookTypeMigratorBase, self).get_at_field_values(old_object):
            yield item

        for fieldname in self.get_old_schemaextender_fieldnames(old_object):
            if fieldname in self.ignore_fields:
                continue
            if not hasattr(aq_base(old_object), fieldname):
                continue
            value = getattr(old_object, fieldname, None)
            if value:
                value = self.normalize_at_field_value(None, fieldname, value)
                yield fieldname, value


class BookMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
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
                (self.migrate_last_modifier, )
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

    def get_old_schemaextender_fieldnames(self, old_object):
        fieldnames = super(BookMigrator, self).get_old_schemaextender_fieldnames(old_object)
        fieldnames += list(getattr(self.get_layout_module(old_object.latex_layout),
                                   'OLD_FIELDNAMES'))
        fieldnames.append('content_categories')
        return fieldnames


class ChapterMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
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
                 self.migrate_last_modifier,
                 self.migrate_chapter_files)
                + additional_steps),
            **kwargs
        )
        self.steps_before_clone += (
            self.move_listingblock_images_to_chapter,
        )

    def query(self):
        return {'portal_type': 'Chapter', 'sort_on': 'path'}

    def move_listingblock_images_to_chapter(self, old_object):
        # Images in listingblocks are no longer support and the book
        # does not support a gallery block.
        # Thus we need to move to the chapter and the ImageToBookTextBlockMigrator
        # will convert it to a textblock so that it is visible in the book.
        listingblocks = old_object.listFolderContents(contentFilter={
            'portal_type': ['ListingBlock', 'ftw.book.FileListingBlock']})
        for listingblock in listingblocks:
            images = listingblock.listFolderContents(contentFilter={'portal_type': ['Image']})
            for image in images:
                api.content.move(source=image, target=old_object, safe_id=True)

    def migrate_chapter_files(self, old_page, new_page):
        files = old_page.listFolderContents(contentFilter={'portal_type': ['File', 'ftw.file.File']})
        if not files:
            return

        listingblock = createContentInContainer(
            container=new_page,
            portal_type='ftw.book.FileListingBlock',
            title='Auflistungsblock',
            show_title=False,
            hide_from_toc=True,
            columns=['getContentType', 'Title'])

        for obj in files:
            api.content.move(source=obj, target=listingblock, safe_id=True)


class BookTextBlockMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
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
                (self.migrate_sl_image_layout,
                 self.migrate_last_modifier)
                + additional_steps),
            **kwargs
        )

    def query(self):
        return {'portal_type': 'BookTextBlock'}

    def get_old_schemaextender_fieldnames(self, old_object):
        fieldnames = super(BookTextBlockMigrator, self).get_old_schemaextender_fieldnames(old_object)
        # izug.latex extension
        fieldnames.append('adjudicationDate')
        return fieldnames


class BookListingBlockMigrator(BookTypeMigratorBase):
    # WARNING: Needs to be run before ImageToBookTextBlockMigrator

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        super(BookListingBlockMigrator, self).__init__(
            new_portal_type='ftw.book.FileListingBlock',
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
                'sortOn': 'sort_on',
                'sortOrder': 'sort_order',
                'tableColumns': 'columns',
            },
            additional_steps=(
                (self.migrate_last_modifier,)
                + additional_steps),
            **kwargs)

    def query(self):
        return {'portal_type': 'ListingBlock', 'path': get_book_paths()}


class ImageToBookTextBlockMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        super(ImageToBookTextBlockMigrator, self).__init__(
            new_portal_type='ftw.book.TextBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields + (
                    'lastModifier',
                    'description',
                    'searchwords',
                    'showinsearch')),
            additional_steps=(
                (self.migrate_sl_image_layout,
                 self.migrate_last_modifier)
                + additional_steps),
            **kwargs)

    def migrate_object(self, old_object):
        if aq_parent(aq_inner(old_object)).portal_type not in ['Chapter', 'ftw.book.Chapter']:
            # Only migrate images in chapters.
            return
        return super(ImageToBookTextBlockMigrator, self).migrate_object(old_object)

    def query(self):
        return {'portal_type': 'Image', 'path': get_book_paths()}

    def get_at_field_values(self, old_object):
        for item in super(ImageToBookTextBlockMigrator, self).get_at_field_values(old_object):
            yield item

        yield 'show_title', False
        yield 'hide_from_toc', True


class HTMLBlockMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
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
                (self.migrate_last_modifier, )
                + additional_steps),
            **kwargs)

    def query(self):
        return {'portal_type': 'HTMLBlock', 'path': get_book_paths()}


class TableMigrator(BookTypeMigratorBase):

    def __init__(self, ignore_fields=(), additional_steps=(), **kwargs):
        super(TableMigrator, self).__init__(
            new_portal_type='ftw.book.Table',
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
                'borderLayout': 'border_layout',
                'columnProperties': 'column_properties',
                'firstColumnIsHeader': 'first_column_is_header',
                'footerIsBold': 'footer_is_bold',
                'footerRows': 'footer_rows',
                'footnoteText': 'footnote_text',
                'headerRows': 'header_rows',
                'noLifting': 'no_lifting',
                'showTitle': 'show_title',
            },
            additional_steps=(
                (self.migrate_last_modifier, )
                + additional_steps),
            **kwargs)

    def query(self):
        return {'portal_type': 'Table'}

    def get_field_values(self, old_object):
        for name, value in super(TableMigrator, self).get_field_values(old_object):
            if name == 'columnProperties':
                value = deepcopy(value)
                for item in value:
                    item.pop('columnTitle', None)
                    item['active'] = bool(item['active'])
                    item['bold'] = bool(item['bold'])
                    if item['width']:
                        item['width'] = int(item['width'].replace('%', '').strip())
                    else:
                        item['width'] = None
                yield name, value

            else:
                yield name, value

    def get_old_schemaextender_fieldnames(self, old_object):
        fieldnames = super(TableMigrator, self).get_old_schemaextender_fieldnames(old_object)
        # izug.latex extension
        fieldnames.extend([
            'lift_table',
            'data',
            'columnProperties',
        ])
        return fieldnames
