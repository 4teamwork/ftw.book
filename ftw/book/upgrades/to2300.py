from ftw.upgrade import UpgradeStep


class UpdateCatalogMetadata(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.book.upgrades:2300')
