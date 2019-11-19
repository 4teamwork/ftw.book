from collective.transmogrifier import transmogrifier
from datetime import datetime
from ftw.book.tests.builders import asset
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from ftw.builder import ticking_creator
from ftw.builder.testing import functional_session_factory
from ftw.testing import freeze
from ftw.testing import IS_PLONE_5
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.globalrequest import getRequest
import ftw.file.tests.builders  # noqa
import transaction


def clear_transmogrifier_registry():
    transmogrifier.configuration_registry._config_info = {}
    transmogrifier.configuration_registry._config_ids = []


class BookLayer(PloneSandboxLayer):
    """The new dexterity book testing layer, providing a default
    book for testing against.
    """

    defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

    def setUp(self):
        session.current_session = functional_session_factory()
        super(BookLayer, self).setUp()

    def tearDown(self):
        session.current_session = None
        super(BookLayer, self).tearDown()
        clear_transmogrifier_registry()

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.book.tests" file="examplecontent.zcml" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.book')
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.book:default')
        applyProfile(portal, 'ftw.zipexport:default')
        self['example_book_path'] = '/'.join(
            self.create_example_book().getPhysicalPath())
        self['default_layout_book_path'] = '/'.join(
            self.create_default_layout_book().getPhysicalPath())

    def create_example_book(self):
        transaction.commit()
        with freeze(datetime(2016, 10, 31, 9, 52, 34)) as clock:
            create = ticking_creator(clock, hours=1)

            book = create(Builder('book').titled(u'The Example Book'))

            introduction = create(Builder('chapter').within(book)
                                  .titled(u'Introduction'))

            create(Builder('book textblock').within(introduction)
                   .titled(u'Invisible Title')
                   .having(show_title=False))

            create(Builder('book textblock').within(introduction)
                   .titled(u'Versioning')
                   .having(show_title=True,
                           hide_from_toc=True))

            create(Builder('book textblock').within(introduction)
                   .with_default_content()
                   .titled(u'Management Summary')
                   .having(show_title=True))

            create(Builder('book htmlblock').within(introduction)
                   .titled('An HTML Block')
                   .having(show_title=False,
                           content='<p>Some <b>bold</b> and <i>italic</i> text.'))

            history = create(Builder('chapter').within(book)
                             .titled(u'Historical Background'))
            china = create(Builder('chapter').within(history)
                           .titled(u'China'))
            create(Builder('book textblock').within(china)
                   .titled(u'First things first')
                   .with_text(u'<p>This is <i>some</i> text.</p>')
                   .with_image(asset('image.jpg')))

            create(Builder('table')
                   .titled(u'Population')
                   .with_table((('Ranking', 'City', 'Population'),
                                ('1', 'Guangzhou', '44 mil <sup>1</sup>'),
                                ('2', 'Shanghai', '35 mil'),
                                ('3', 'Chongqing', '30 mil')))
                   .having(border_layout='grid',
                           footnote_text=RichTextValue(
                               u'<p><sup>1</sup> thats quite big</p>'))
                   .within(china))

            listingblock = create(
                Builder('book listingblock')
                .titled(u'Important Documents')
                .within(china))

            create(Builder('file')
                   .within(listingblock)
                   .titled(u'Fr\xf6hliches Bild')
                   .attach_file_containing(asset('image.jpg').bytes(), u'image.jpg'))

            create(Builder('file')
                   .within(listingblock)
                   .titled(u'Einfache Webseite')
                   .attach_file_containing(asset('lorem.html').bytes(), u'lorem.html'))

            create(Builder('chapter').within(book)
                   .titled(u'Empty')
                   .having(description=u'This chapter should be empty.'))

        return book

    def create_default_layout_book(self):
        return create(
            Builder('book')
            .titled(u'The Default Layout Book')
            .having(
                web_toc_depth=3,
                latex_layout='ftw.book.latex.defaultlayout.IDefaultBookLayout',
                use_titlepage=True,
                use_toc=True,
                use_lot=True,
                use_loi=True,
                use_index=True,
                release=u'1.7.2',
                book_author=u'Mr. Smith',
                author_address=u'Smith Consulting\nSwordstreet 1'
                u'\n1234 Anvil City',
                titlepage_logo=NamedBlobImage(
                    filename=u'smith.jpg',
                    data=asset('smith.jpg').bytes()),
                titlepage_logo_width=25,
            ))


BOOK_FIXTURE = BookLayer()
BOOK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BOOK_FIXTURE,),
    name="ftw.book:functional")


class LatexZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES, )

    def testSetUp(self):
        import ftw.book.tests
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        xmlconfig.file('latex.zcml', ftw.book.tests,
                       context=self['configurationContext'])

    def testTearDown(self):
        del self['configurationContext']


LATEX_ZCML_LAYER = LatexZCMLLayer()


class LanguageSetter(object):

    def set_language_settings(self, default='en', supported=None,
                              use_combined=False, start_neutral=True):
        """
        Sets language settings regardeless if plone4.3 or plone5.1
        :param default: default site language
        :param supported: list of supported languages
        """
        # startNeutral is not used/available in plone 5.1 anymore

        if not supported:
            supported = [default]

        if IS_PLONE_5:
            from Products.CMFPlone.interfaces import ILanguageSchema

            self.ltool = api.portal.get_tool('portal_languages')
            self.ltool.settings.use_combined_language_codes = use_combined
            for lang in supported:
                self.ltool.addSupportedLanguage(lang)
            self.ltool.setDefaultLanguage(default)
            self.ltool.setLanguageCookie()
            self._set_preferred_language(default)
            registry = getUtility(IRegistry)
            language_settings = registry.forInterface(
                    ILanguageSchema, prefix='plone')
            language_settings.use_content_negotiation = True
        else:
            self.ltool = api.portal.get().portal_languages
            self.ltool.manage_setLanguageSettings(
                default,
                supported,
                setUseCombinedLanguageCodes=use_combined,
                # Set this only for better testing ability
                setCookieEverywhere=True,
                startNeutral=start_neutral,
                setContentN=True)
        transaction.commit()

    def _set_preferred_language(self, default):
        from plone.i18n.utility import LanguageBinding
        request = getRequest()
        binding = request.get("LANGUAGE_TOOL", None)
        if isinstance(binding, LanguageBinding):
            binding.LANGUAGE = default
