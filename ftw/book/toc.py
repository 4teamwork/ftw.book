from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book.behaviors.toc import IHideTitleFromTOC
from ftw.book.behaviors.toc import IShowInToc
from ftw.book.interfaces import IBook
import cgi


class TableOfContents(object):

    def html_heading(self, context, classes=None, linked=False,
                     tagname=None, prepend_html_headings=False):
        """Returns a HTML representation of the heading of the context.
        The HTML-heading has the correct level.
        Additional classes may be mixed in.
        """
        if not self.visible(context) or not self.in_book(context):
            return None

        if classes:
            classes = list(classes)
        else:
            classes = []

        level = self.level(context)

        if not self.in_toc(context):
            classes.append('no-toc')
        else:
            classes.append('toc{}'.format(level))

        title = cgi.escape(context.Title())
        if linked:
            inner = '<a href="{}">{}</a>'.format(
                context.absolute_url(), title)
        else:
            inner = title

        if tagname is None:
            tagname = 'h{}'.format(level)

        if prepend_html_headings:
            prepend_html = '{}\n'.format(
                self.prepend_html_headings(context))
        else:
            prepend_html = ''

        return '{pre}<{tag} class="{classes}">{inner}</{tag}>'.format(
            pre=prepend_html,
            tag=tagname,
            classes=' '.join(sorted(classes)),
            inner=inner)

    def prepend_html_headings(self, context):
        """HTML headings for prepending to the context heading so that the
        CSS counters are incremented correctly.
        """
        html = []

        parents = filter(self.in_toc, aq_chain(aq_parent(context)))
        for parent in reversed(parents):
            # Use contentValues for implicit ftw.trash support.
            for child in filter(self.in_toc, parent.contentValues()):
                if child == context:
                    break

                html.append(self.html_heading(child,
                                              classes=['hiddenStructure']))
                if child in parents:
                    break

        return '\n'.join(html)

    def in_toc(self, context):
        """Returns `True` if the object is shown in the table of contents.
        """
        if not IShowInToc.providedBy(context):
            return False

        if not self.visible(context):
            return False

        if getattr(IHideTitleFromTOC(context, None), 'hide_from_toc', None):
            return False

        return True

    def in_book(self, context):
        """Returns ``True`` when the context is within a book or if it is
        the book itself.
        """
        return self.book(context) is not None

    def visible(self, context):
        """Returns ``True`` if the object title is visible in the body.
        The title may be hidden from the table of contents though.
        """
        return getattr(context, 'show_title', None) is not False

    def level(self, context):
        """Return the level of this context when it is listed in the toc.
        The book has the level 1, chapters have index 2,
        sections have index 3, etc.
        """

        book = self.book(context)
        if book is None:
            return None
        else:
            return aq_chain(context).index(book) + 1

    def index(self, context):
        """Return the index of this context within its parent.
        Returns an integer when the context is contained in the toc and
        ``None`` when it is not.
        Starts with 1: the first (sub)chapter of a context has
        the index 1, the second has the index 2, etc.
        """
        if not self.in_toc(context):
            return None

        # The book has no number.
        if IBook.providedBy(context):
            return None

        parent = aq_parent(aq_inner(context))
        # Use contentValues for implicit ftw.trash support.
        siblings = parent.contentValues()
        contained_siblings = filter(self.in_toc, siblings)
        return contained_siblings.index(context) + 1

    def number(self, context):
        """Returns the chapter number for the context, e.g. "1.3.2".
        ``None`` is returned if the context is not listed in the
        table of contents.
        """
        if self.index(context) is None:
            return None

        return '.'.join(
            map(str,
                map(self.index,
                    self.parent_chapters(context) + [context])))

    def book(self, context):
        """Find the next book in the acquisition chain of the context
        and return it.
        The chain includes itself, so if the context is the book,
        it is returned.
        Return None when the context is not within a book.
        """
        return next(iter(filter(IBook.providedBy, aq_chain(context))), None)

    def parent_chapters(self, context):
        """Returns a list of all parents which are visible in the table of
        contents. Does not include the book nor the context.
        The order is top-down (chapter, subchapter, subsubchapter, ...).
        """
        return list(reversed(filter(lambda obj: not IBook.providedBy(obj),
                                    filter(self.in_toc,
                                           aq_chain(aq_parent(context))))))
