from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from plone.app.blob.field import ImageField
from Products.Archetypes import atapi
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import SelectionWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin


# Schemas copied from ftw.contentpage in order to have the
# fields for migrating from AT to DX while getting rid of
# the ftw.contentpage dependency.

default_schema = atapi.Schema((
    atapi.BooleanField(
        name='showTitle',
        schemata='default',
        default=0,
        widget=atapi.BooleanWidget()),

    atapi.TextField(
        name='text',
        primary=True,
        required=False,
        searchable=True,
        allowable_content_types=('text/html', ),
        default_content_type='text/html',
        validators=('isTidyHtmlWithCleanup', ),
        default_input_type='text/html',
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            allow_file_upload=False,
            rows=25))))


image_schema = atapi.Schema((
    ImageField(
        name='image',
        required=False,
        schemata='image',
        widget=atapi.ImageWidget()),

    atapi.BooleanField(
        name='imageClickable',
        schemata='image',
        default=0,
        widget=atapi.BooleanWidget()),

    atapi.StringField(
        name='imageCaption',
        required=False,
        searchable=True,
        schemata='image',
        widget=atapi.StringWidget()),

    atapi.StringField(
        name='imageAltText',
        schemata='image',
        required=False,
        widget=atapi.StringWidget())))

teaser_schema = atapi.Schema((

    atapi.StringField(
        name='teaserSelectLink',
        schemata='teaser',
        multiValued=False,
        storage=atapi.AttributeStorage(),
        vocabulary=DisplayList((
            ('intern', 'Internal Reference'),
            ('extern', 'External URL'),
        )),
        widget=SelectionWidget()),

    atapi.StringField(
        name='teaserExternalUrl',
        schemata='teaser',
        searchable=False,
        validators='isURL',
        widget=atapi.StringWidget()),

    atapi.ReferenceField(
        name='teaserReference',
        relationship='teasesContent',
        schemata='teaser',
        multiValued=False,
        widget=ReferenceBrowserWidget(
            force_close_on_insert=True))))


textblock_schema = (
    ATContentTypeSchema.copy()
    + default_schema.copy()
    + image_schema.copy()
    + teaser_schema.copy())


class BookTextBlock(ATCTContent, HistoryAwareMixin):
    schema = textblock_schema


atapi.registerType(BookTextBlock, 'ftw.book')
