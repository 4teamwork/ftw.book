import os
from setuptools import setup, find_packages


version = '3.5.0'
maintainer = 'Jonas Baumann'


tests_require = [
    'Products.GenericSetup',
    'ftw.builder',
    'ftw.inflator',
    'ftw.publisher.core',
    'ftw.tabbedview',
    'ftw.testbrowser',
    'ftw.testing',
    'ftw.zipexport',
    'mocker',
    'plone.app.testing',
    'plone.browserlayer',
    'plone.mocktestcase',
    'plone.portlets',
    'plone.testing',
    'transaction',
    'unittest2',
    'zope.app.component',
    'zope.browser',
    'zope.configuration',
    'zope.i18n',
    'zope.traversing',
    'zope.viewlet',
    ]

extras_require = {
    'tests': tests_require,
    'tabbeview': [
        'ftw.tabbedview',
        'ftw.table'],
    'linguaplone': [
        'Products.LinguaPlone']}

setup(name='ftw.book',
      version=version,
      description='Produce books with Plone and export them in a high ' + \
          'quality PDF.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw book pdf plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.book',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'AccessControl',
        'Acquisition',
        'BeautifulSoup!=4.0b',
        'Plone',
        'Products.ATContentTypes',
        'Products.Archetypes',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Products.DataGridField>=1.9',
        'Products.GenericSetup',
        'Products.TinyMCE',
        'Products.statusmessages',
        'Zope2',
        'archetypes.schemaextender',
        'ftw.contentpage !=1.11.0, !=1.11.1',
        'ftw.pdfgenerator>=1.4',
        'ftw.profilehook',
        'ftw.upgrade',
        'lxml',
        'plone.app.contentmenu',
        'plone.app.layout',
        'plone.app.portlets',
        'plone.indexer',
        'plone.portlets',
        'setuptools',
        'simplelayout.base >= 4.0.0',
        'zope.annotation',
        'zope.component',
        'zope.dottedname',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
