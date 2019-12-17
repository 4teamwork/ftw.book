from ftw.book import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class UpdateResourceBundle(UpgradeStep):
    """Update resource bundle.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile()
        else:
            # do not add the registry.xml in plone 4
            pass
