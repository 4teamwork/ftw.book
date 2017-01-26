from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from Products.CMFPlone.utils import getFSVersionTuple
from unittest2 import skip
from unittest2 import TestCase


@skip('XXX UPDATE ME')
@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.book'
    additional_products = (
        'simplelayout.base',
        'simplelayout.ui.base',
        'simplelayout.ui.dragndrop',
        'ftw.contentpage',
        )

    @property
    def skip_files(self):
        if getFSVersionTuple() < (4, 3):
            # Plone <= 4.2 does not support removing thins in tinymce.xml
            return ('tinymce.xml')
        else:
            return ()
