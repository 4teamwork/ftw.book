from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import ploneSite
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.browserlayer.layer import mark_layer
from plone.mocktestcase.dummy import Dummy
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from plone.testing import zodb
from zope.configuration import xmlconfig


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

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.book
        import ftw.book.portlets
        import simplelayout.base
        import simplelayout.types.common
        import ftw.pdfgenerator

        xmlconfig.file('configure.zcml', ftw.book,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', ftw.book.portlets,
                       context=configurationContext)

        xmlconfig.file('configure.zcml', simplelayout.base,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', simplelayout.types.common,
                       context=configurationContext)

        xmlconfig.file('configure.zcml', ftw.pdfgenerator,
                       context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2
        # products, using <five:registerPackage /> in ZCML.
        z2.installProduct(app, 'ftw.book')
        z2.installProduct(app, 'simplelayout.base')
        z2.installProduct(app, 'simplelayout.types.common')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.book:default')
        applyProfile(portal, 'simplelayout.base:default')
        applyProfile(portal, 'simplelayout.types.common:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_BOOK_FIXTURE = FtwBookLayer()
FTW_BOOK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_BOOK_FIXTURE, ), name="FtwBook:Integration")
FTW_BOOK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_BOOK_FIXTURE, ), name="FtwBook:Functional")



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
    bases=(EXAMPLE_CONTENT_FIXTURE, ), name="ftw.book:examplecontent:integration")
