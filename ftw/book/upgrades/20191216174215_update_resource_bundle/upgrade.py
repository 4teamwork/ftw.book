from ftw.book import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class UpdateResourceBundle(UpgradeStep):
    """Update resource bundle.
    """

    def __call__(self):
        # The registry entries only have to be installed on plone 5
        if IS_PLONE_5:
            self.install_upgrade_profile()
