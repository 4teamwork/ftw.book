from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from zope.configuration import xmlconfig


class FtwBookLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.book
        xmlconfig.file('configure.zcml', ftw.book, context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2 products,
        # using <five:registerPackage /> in ZCML.
        z2.installProduct(app, 'ftw.book')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.book:default')


FTW_BOOK_FIXTURE = FtwBookLayer()
FTW_BOOK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_BOOK_FIXTURE,), name="FtwBook:Integration")
