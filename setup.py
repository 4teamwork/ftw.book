import os
from setuptools import setup, find_packages


version = '4.1.8'
maintainer = 'Jonas Baumann'


tests_require = [
    'collective.transmogrifier',
    'ftw.builder',
    'ftw.inflator',
    'ftw.tabbedview',
    'ftw.testbrowser',
    'ftw.testing<2a',
    'ftw.zipexport',
    'plone.app.testing',
    'plone.mocktestcase',
    'transmogrify.dexterity',
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
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.1',
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
          'BeautifulSoup!=4.0b',
          'Plone',
          'collective.z3cform.datagridfield>=1.3.3',
          'ftw.file >= 2.0.1',
          'ftw.htmlblock>=1.1.0',
          'ftw.pdfgenerator>=1.4',
          'ftw.profilehook',
          'ftw.simplelayout >= 2.1.0',
          'ftw.upgrade',
          'lxml',
          'setuptools',
      ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """)
