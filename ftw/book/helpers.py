from Acquisition import aq_inner, aq_parent
from ftw.book.interfaces import IBook
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.interfaces._content import IFolderish


class Numbering(object):

    def __call__(self, obj):
        return self.generate_title(obj)

    def generate_title(self, obj):
        """ Generates a title embedded in a h-tag
        """
        chapter_string = self.get_chapter_level_string(obj)
        title = obj.title_or_id()
        hierarchy = self.get_hierarchy_position(obj)
        title = "<h%s>%s %s</h%s>" % (
            hierarchy, chapter_string, title, hierarchy)

        return title

    def generate_valid_parent_h_tags(self, obj):
        """ Generates the h-tags for parent-objects for valid html
        """
        titles = self._get_parent_titles(obj)
        html = ""

        for i, title in enumerate(titles):
            html += '<h%s>%s</h%s>' % (i+1, title, i+1)
        return html

    def get_chapter_level_string(self, obj):
        """ Return the string of the chapter levele: 1.4.3
        """
        chapter_level = self._get_chapter_level(obj)
        chapter_level = [str(level) for level in chapter_level]
        return '.'.join(chapter_level)

    def get_folder_position(self, obj):
        """ Get the position of the object in the folder
        """
        return self._get_filtered_folder_position(obj)

    def get_hierarchy_position(self, obj):
        """ Get the position in the hierarchy of the book
        """
        return self._get_hierarchy_position(obj)

    def _get_chapter_level(self, obj):
        """ Return the chapterlevel in a dict
        of int
        """
        chapter_level = []
        parent = obj
        while not IPloneSiteRoot.providedBy(parent):
            if IBook.providedBy(parent):
                break
            else:
                chapter_level.append(
                    self._get_filtered_folder_position(parent))
                parent = aq_parent(aq_inner(parent))

        chapter_level.reverse()

        return chapter_level

    def _get_parent_titles(self, obj):
        """ Get all titles of parent in a list: ['first', 'second']
        """
        titles = []
        parent = obj
        while not IPloneSiteRoot.providedBy(parent):
            titles.append(parent.Title())
            if IBook.providedBy(parent):
                break
            else:
                parent = aq_parent(aq_inner(parent))

        titles.reverse()
        return titles

    def _get_hierarchy_position(self, obj):
        """ Get the hierarchy position of the object as int
        """
        position = 1
        parent = obj
        while not IPloneSiteRoot.providedBy(parent):
            if IBook.providedBy(parent):
                break
            else:
                position += 1
                parent = aq_parent(aq_inner(parent))

        return position

    def _get_filtered_folder_position(self, obj):
        """ Return the filtered folder position as int
        """

        consider_types = ['BookParagraph', 'Chapter']
        parent = aq_parent(aq_inner(obj))
        counter = 0

        if not IFolderish.providedBy(parent):
            return counter

        folder_content = parent.listFolderContents()

        for item in folder_content:

            if hasattr(item, 'showTitle') and not item.showTitle:
                continue

            if item.portal_type in consider_types:
                counter += 1

            if obj == item:
                break

        return counter
