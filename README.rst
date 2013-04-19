ftw.book
========

This package provides content types for creating a book which can be exported as PDF.

.. figure:: http://onegov.ch/approved.png/image
   :align: right
   :target: http://onegov.ch/community/zertifizierte-module/ftw.book

   Certified: 01/2013


Features
--------

- Provides a content type "Book" which defines the root of a book.
- Provides a content type "Chapter" for creating the structure of a book. Chapters are nestable.
- Content is added to chapters using simplelayout blocks.
- Provides an action for exporting the book or a single chapter recursively as PDF.
- Provides LaTeX representations for the default simplelayout blocks.
- Adds fields for injecting LaTeX code to every content type within a book using schemaextender.
- Provides a "Reader" view which displays the book on one page for a enjoyable reading experience.
- Provides simplalayout "Table" block for enter tabular data using a datagrid widget which generates
  HTML table representation which also convertable into a PDF.


Usage
-----

- Add ``ftw.book`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.book

- Install the generic import profile.

- Install a LaTeX distribution, see `ftw.pdfgenerator`_  install instructions.


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.1`, `4.2` or `4.3`.


Development / tests
-------------------

For running the full PDF generation tests `ImageMagick`_ is required for diffing
the PDFs.


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.book
- Issue tracker: https://github.com/4teamwork/ftw.book/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.book
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.book


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.book`` is licensed under GNU General Public License, version 2.

.. _ftw.pdfgenerator: https://github.com/4teamwork/ftw.pdfgenerator
.. _ImageMagick: http://cactuslab.com/imagemagick/

.. image:: https://cruel-carlota.pagodabox.com/7b44b1a6f894bf7555c54e95144cc43d
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.book
