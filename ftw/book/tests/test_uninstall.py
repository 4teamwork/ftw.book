from ftw.testing.genericsetup import GenericSetupUninstallMixin
from ftw.testing.genericsetup import apply_generic_setup_layer
from unittest2 import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.book'
    additional_products = (
        'simplelayout.base',
        'simplelayout.ui.base',
        'simplelayout.ui.dragndrop',
        'ftw.contentpage',
        )
