from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from unittest2 import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.book'
