ftw.book
========

This package provides content types for creating a book, which can be exported as PDF.


Features
--------

 - Provides a content type "Book" which defines the root of a book.
 - Provides a content type "Chapter" for creating the structure of a book. Chapters are nestable.
 - Content is added to chapters using simplelayout blocks.
 - Provides an action for exporting the book or a single chapter recursively as PDF.
 - Provides LaTeX representations for the default simplelayout blocks.
 - Adds fields for injecting LaTeX code to every content type within a book using schemaextender.

