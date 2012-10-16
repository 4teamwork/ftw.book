import os
from setuptools import setup, find_packages


version = '2.2.9'
maintainer = 'Jonas Baumann'


tests_require = [
    'zope.testing',
    'plone.app.testing',
    'plone.mocktestcase',
    'plone.portlets',
    'ftw.testing',
    'pyquery',
    ]

extras_require = {
    'tests': tests_require,
    'tabbeview': [
        'ftw.tabbedview'],
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
        'simplelayout.types.common',
        'simplelayout.base',
        'archetypes.schemaextender',
        'plone.portlets',
        'ftw.pdfgenerator',
        'BeautifulSoup!=4.0b',
        'Products.DataGridField',
        'ftw.upgrade',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
