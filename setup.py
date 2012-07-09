import os
from setuptools import setup, find_packages


version = '2.2.7.dev0'
maintainer = 'Jonas Baumann'


tests_require = [
    'Products.GenericSetup',
    'ftw.testing',
    'mocker',
    'plone.app.testing',
    'plone.mocktestcase',
    'plone.portlets',
    'plone.testing',
    'pyquery',
    'unittest2',
    'z3c.autoinclude',
    'zope.app.component',
    'zope.browser',
    'zope.configuration',
    'zope.i18n',
    'zope.traversing',
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
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw book pdf plone',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://github.com/4teamwork/ftw.book',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'AccessControl',
        'Acquisition',
        'BeautifulSoup!=4.0b',
        'Products.ATContentTypes',
        'Products.Archetypes',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Products.DataGridField',
        'Products.statusmessages',
        'Zope2',
        'archetypes.schemaextender',
        'ftw.pdfgenerator',
        'plone.app.contentmenu',
        'plone.app.layout',
        'plone.app.portlets',
        'plone.portlets',
        'simplelayout.base',
        'simplelayout.types.common',
        'zope.component',
        'zope.dottedname',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.viewlet',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
