from ftw.upgrade import UpgradeStep


class AddBookKeyword(UpgradeStep):

    def __call__(self):
        # Install metadata
        self.setup_install_profile(
            'profile-ftw.book.upgrades:3002', steps=['catalog'])

        # Install index
        catalog = self.getToolByName('portal_catalog')
        catalog.addIndex('book_keywords', 'KeywordIndex')

        # Reindex index and metadata
        self.catalog_reindex_objects({'portal_type': 'BookTextBlock'},
                                     idxs=['book_keywords'])
