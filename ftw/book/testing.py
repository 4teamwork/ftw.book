from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from zope.configuration import xmlconfig
from plone.testing import Layer
from plone.testing import zca
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD, login


class FtwBookLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

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
    bases=(FTW_BOOK_FIXTURE,), name="FtwBook:Integration")



class BasicMockRendererLayer(Layer):

    defaultBases = (z2.FUNCTIONAL_TESTING, )

    def setUp(self):
        super(BasicMockRendererLayer, self).setUp()

        import pdb; pdb.set_trace( )
        self['configurationContext'] = context = zca.stackConfigurationContext(self.get('configurationContext'))
        import zope.traversing
        xmlconfig.file(
            'configure.zcml',
            zope.traversing,
            context=context)
        import plone.portlets
        xmlconfig.file(
            'configure.zcml',
            plone.portlets,
            context=context)
        
        # import ftw.workspace
        # xmlconfig.file(
        #     'configure.zcml',
        #     ftw.workspace,
        #     context=context)


RENDERER_LAYER = BasicMockRendererLayer()        

