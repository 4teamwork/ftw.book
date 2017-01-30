from collective.transmogrifier import transmogrifier
from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import ploneSite
from plone.browserlayer.layer import mark_layer
from plone.mocktestcase.dummy import Dummy
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from plone.testing import zodb
from zope.configuration import xmlconfig
import ftw.book.tests.builders
import ftw.contentpage.tests.builders


def clear_transmogrifier_registry():
    transmogrifier.configuration_registry._config_info = {}
    transmogrifier.configuration_registry._config_ids = []


class BookLayer(PloneSandboxLayer):
    """The new dexterity book testing layer, providing a default
    book for testing against.
    """

    defaultBases = (PLONE_FIXTURE,)

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
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.book')
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.book:default')
        self['example_book_path'] = '/'.join(
            self.create_example_book().getPhysicalPath())

    def create_example_book(self):
        book = create(Builder('book').titled(u'The Example Book'))

        introduction = create(Builder('chapter').within(book)
                              .titled(u'Introduction'))

        create(Builder('book textblock').within(introduction)
               .titled(u'Invisible Title').with_default_content()
               .having(show_title=False))

        create(Builder('book textblock').within(introduction)
               .titled(u'Versioning')
               .having(show_title=True,
                       hide_from_toc=True))

        create(Builder('book textblock').within(introduction)
               .titled(u'Management Summary')
               .having(show_title=True))

        history = create(Builder('chapter').within(book)
                         .titled(u'Historical Background'))
        china = create(Builder('chapter').within(history)
                       .titled(u'China'))
        create(Builder('book textblock').within(china)
               .titled(u'First things first'))

        create(Builder('chapter').within(book)
               .titled(u'Empty')
               .having(description=u'This chapter should be empty.'))

        return book


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


class ZCMLLayer(ComponentRegistryLayer):
    """Test layer loading the complete package ZCML.
    """

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        import ftw.book.tests
        self.load_zcml_file('test.zcml', ftw.book.tests)


ZCML_LAYER = ZCMLLayer()


class FtwBookLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.book')
        z2.installProduct(app, 'simplelayout.base')
        z2.installProduct(app, 'ftw.contentpage')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.book:default')
        applyProfile(portal, 'ftw.tabbedview:default')
        applyProfile(portal, 'ftw.zipexport:default')

    def tearDown(self):
        super(FtwBookLayer, self).tearDown()
        clear_transmogrifier_registry()


FTW_BOOK_FIXTURE = FtwBookLayer()
FTW_BOOK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_BOOK_FIXTURE, ), name="ftw.book:Integration")
FTW_BOOK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_BOOK_FIXTURE,
           set_builder_session_factory(functional_session_factory)
    ), name="ftw.book:Functional (OLD)")


class ExampleContentLayer(Layer):

    defaultBases = (FTW_BOOK_FIXTURE, )

    def setUp(self):
        # Stack the component registry
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        # Stack the database
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'), name='ftw.book:examplecontent')

        # Register and apply the example content GS profile
        import ftw.book.tests
        xmlconfig.file('examplecontent.zcml', ftw.book.tests,
                       context=self['configurationContext'])

        with ploneSite() as portal:
            request = portal.REQUEST
            mark_layer(None, Dummy(request=request))
            provide_request_layer(request, IWithinBookLayer)
            provide_request_layer(request, IDefaultBookLayoutSelectionLayer)

            applyProfile(portal, 'ftw.book.tests:examplecontent')

    def tearDown(self):
        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']
        # Zap the stacked component registry
        del self['configurationContext']


EXAMPLE_CONTENT_FIXTURE = ExampleContentLayer()
EXAMPLE_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EXAMPLE_CONTENT_FIXTURE, ),
    name="ftw.book:examplecontent:integration")
