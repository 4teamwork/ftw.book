from ftw.upgrade import UpgradeStep
from operator import methodcaller


class MigrateParagraphs(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-ftw.book.upgrades:3000')

        query = {'path': self.get_book_paths(),
                 'portal_type': 'Paragraph'}
        for obj in self.objects(query, 'Migrate Paragraph to BookTextBlock'):
            self.migrate_paragraph(obj)

    def get_book_paths(self):
        return map(methodcaller('getPath'),
                   self.catalog_unrestricted_search({'portal_type': 'Book'}))

    def migrate_paragraph(self, obj):
        from ftw.book.content.textblock import BookTextBlock
        self.migrate_class(obj, BookTextBlock)
        obj.portal_type = 'BookTextBlock'
        obj.reindexObject()
