ftw.book
========

This package provides content types for creating a book which can be exported as PDF.


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


Requirements
------------

- Requires `ftw.simplelayout`_ for block based content creation.
- Requires `ftw.file`_ for file listings.
- Requires `ftw.pdfgenerator`_ for generating PDFs.
- Requires `ftw.htmlblock`_ for custom HTML tables.


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

Runs with `Plone <http://www.plone.org/>`_ `4.3` and `5.1`.


Development / tests
-------------------

For running the full PDF generation tests `ImageMagick`_ is required for diffing
the PDFs.

Since we need to re-compile the resources after each change, there is a
watcher implemented started with ``yarn watch`` recompiling after each change.

Uninstall
---------

This package provides an uninstall Generic Setup profile, however, it will
not uninstall the package dependencies.
Make sure to uninstall the dependencies if you no longer use them.


Links
-----

- Github: https://github.com/4teamwork/ftw.book
- Issues: https://github.com/4teamwork/ftw.book/issues
- Pypi: http://pypi.python.org/pypi/ftw.book
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.book


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.book`` is licensed under GNU General Public License, version 2.

.. _ftw.file: https://github.com/4teamwork/ftw.file
.. _ftw.htmlblock: https://github.com/4teamwork/ftw.htmlblock
.. _ftw.pdfgenerator: https://github.com/4teamwork/ftw.pdfgenerator
.. _ftw.simplelayout: https://github.com/4teamwork/ftw.simplelayout
.. _ImageMagick: http://cactuslab.com/imagemagick/
