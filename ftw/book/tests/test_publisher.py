from ftw.book.interfaces import IWithinBookLayer
from ftw.book.latex.defaultlayout import IDefaultBookLayoutSelectionLayer
from ftw.book.testing import FTW_BOOK_INTEGRATION_TESTING
from ftw.builder import Builder
from ftw.builder import create
from ftw.publisher.core.interfaces import IDataCollector
from unittest2 import TestCase
from zope.component import getAdapter
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides


class TestBookLayoutRequestLayerCollector(TestCase):
    layer = FTW_BOOK_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']

    def test_getData_sets_request_layers(self):
        book = create(Builder('book').with_layout(IDefaultBookLayoutSelectionLayer))

        self.remove_request_interfaces()
        self.assertFalse(IDefaultBookLayoutSelectionLayer.providedBy(self.request))
        self.assertFalse(IWithinBookLayer.providedBy(self.request))
        collector = getAdapter(book, IDataCollector, name='010-book-layout-request-layers')
        collector.getData()
        self.assertTrue(IDefaultBookLayoutSelectionLayer.providedBy(self.request))
        self.assertTrue(IWithinBookLayer.providedBy(self.request))

    def test_getData_returns_request_layer_dottednames(self):
        book = create(Builder('book').with_layout(IDefaultBookLayoutSelectionLayer))

        collector = getAdapter(book, IDataCollector, name='010-book-layout-request-layers')
        self.assertItemsEqual(
            ['ftw.book.interfaces.IWithinBookLayer',
             'ftw.book.latex.defaultlayout.IDefaultBookLayoutSelectionLayer'],
            collector.getData())

    def test_setData_sets_request_layers(self):
        book = create(Builder('book').with_layout(IDefaultBookLayoutSelectionLayer))

        collector = getAdapter(book, IDataCollector, name='010-book-layout-request-layers')
        data = collector.getData()

        self.remove_request_interfaces()
        self.assertFalse(IDefaultBookLayoutSelectionLayer.providedBy(self.request))
        self.assertFalse(IWithinBookLayer.providedBy(self.request))

        collector.setData(data, {})
        self.assertTrue(IDefaultBookLayoutSelectionLayer.providedBy(self.request))
        self.assertTrue(IWithinBookLayer.providedBy(self.request))

    def remove_request_interfaces(self):
        # Remove custom book interfaces from request
        to_remove = [IWithinBookLayer, IDefaultBookLayoutSelectionLayer]
        ifaces = [iface for iface in directlyProvidedBy(self.request)
                  if iface not in to_remove]
        directlyProvides(self.request, *ifaces)
