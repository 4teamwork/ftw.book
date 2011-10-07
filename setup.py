import os
from setuptools import setup, find_packages


version = open('ftw/book/version.txt').read().strip()
maintainer = 'Julian Infanger'


tests_require = [
    'zope.testing',
    'plone.app.testing',
    'plone.mocktestcase',
    'plone.portlets'
    ]


setup(name='ftw.book',
      version=version,
      description='This package provides content types for ' + \
          'creating a book, which can be exported as PDF.' + \
          ' (Maintainer %s)' % maintainer,

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw book',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://github.com/4teamwork',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'simplelayout.types.common',
        'simplelayout.base',
        'plonegov.pdflatex',
        'archetypes.schemaextender',
        'plone.portlets'
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
