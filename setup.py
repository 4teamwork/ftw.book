# -*- coding: utf-8 -*-
"""
This module contains the tool of ftw.book
"""
import os
from setuptools import setup, find_packages

version = open('ftw/book/version.txt').read().strip()
maintainer = 'Julian Infanger'

tests_require=['zope.testing']

setup(name='ftw.book',
      version=version,
      description="" + \
          ' (Maintainer %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='https://svn.4teamwork.ch/repos/ftw/ftw.book/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plonegov.pdflatex',
                        'simplelayout.base',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'ftw.book.tests.test_docs.test_suite',
      )
