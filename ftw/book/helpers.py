from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book.behaviors.toc import IHideTitleFromTOC
from ftw.book.behaviors.toc import IShowInToc
from ftw.book.interfaces import IBook
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class BookHelper(object):

    def __call__(self, obj, linked=False):
        return self.generate_title(obj, linked=linked)

    def generate_title(self, obj, linked=False):
        """ Generates a title embedded in a h-tag
        """

        if self.is_numbered(obj):
            chapter_string = self.get_chapter_level_string(obj)
        else:
            chapter_string = ''

        title = obj.Title()

        html = ' '.join((chapter_string, title)).strip()
        if linked:
            html = '<a href="%s">%s</a>' % (obj.absolute_url(), html)

        hierarchy = self.get_hierarchy_position(obj)
        html = "<h%s>%s</h%s>" % (
            hierarchy, html, hierarchy)

        return html

    def generate_valid_hierarchy_h_tags(self, obj):
        """ Generates the h-tags for parent-objects for valid html
        """
        titles = self._get_hierarchy_titles(obj)
        html = ""

        for i, title in enumerate(titles):
            html += '<h%s>%s</h%s>' % (i + 1, title, i + 1)
        return html

    def get_hierarchy_position(self, obj):
        """ Get the position in the hierarchy of the book
        """
        return self._get_hierarchy_position(obj)

    def get_chapter_level_string(self, obj):
        """ Return the string of the chapter levele: 1.4.3
        """
        chapter_level = self.get_chapter_level(obj)
        chapter_level = [str(level) for level in chapter_level]
        return '.'.join(chapter_level)

    def get_chapter_level(self, obj):
        """ Return the chapterlevel in a list
        of int
        """
        chapter_level = []
        parent = obj

        while not IPloneSiteRoot.providedBy(parent):
            if IBook.providedBy(parent):
                break
            else:
                chapter_level.insert(
                    0, self._get_filtered_folder_position(parent))
                parent = aq_parent(aq_inner(parent))

        return chapter_level

    def is_numbered(self, obj):
        if not IShowInToc.providedBy(obj):
            return False

        if getattr(obj, 'show_title', None) == False:
            return False

        if IHideTitleFromTOC.providedBy(obj):
            return not IHideTitleFromTOC(obj).hide_from_toc
        else:
            return True

    def _get_hierarchy_titles(self, obj):
        """ Get all titles in the hierarchy in a list: ['first', 'second']
        """
        titles = []
        parent = obj
        while not IPloneSiteRoot.providedBy(parent):
            titles.insert(0, parent.Title())
            if IBook.providedBy(parent):
                break
            else:
                parent = aq_parent(aq_inner(parent))

        return titles

    def _get_hierarchy_position(self, obj):
        """ Get the hierarchy position of the object as int
        """

        position = len(self._get_hierarchy_titles(obj))
        return position < 6 and position or 6

    def _get_filtered_folder_position(self, obj):
        """ Return the filtered folder position as int
        """

        parent = aq_parent(aq_inner(obj))
        counter = 0

        folder_content = parent.contentValues()

        for item in folder_content:
            if self.is_numbered(item):
                counter += 1

            if obj == item:
                break

        return counter
