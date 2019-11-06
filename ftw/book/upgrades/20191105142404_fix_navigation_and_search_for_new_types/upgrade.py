from ftw.upgrade import UpgradeStep


class FixNavigationAndSearchForNewTypes(UpgradeStep):
    """Fix navigation and search for new types.
    """

    def __call__(self):
        self.install_upgrade_profile()
