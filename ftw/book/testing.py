from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
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

        xmlconfig.file('configure.zcml', ftw.book,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', ftw.book.portlets,
                       context=configurationContext)

        xmlconfig.file('configure.zcml', simplelayout.base,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', simplelayout.types.common,
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
