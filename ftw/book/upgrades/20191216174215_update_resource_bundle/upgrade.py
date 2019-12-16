from ftw.upgrade import UpgradeStep


class UpdateResourceBundle(UpgradeStep):
    """Update resource bundle.
    """

    def __call__(self):
        self.install_upgrade_profile()
