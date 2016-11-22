from ftw.upgrade import UpgradeStep


class InstallFtwSimplelayout(UpgradeStep):
    """Install ftw.simplelayout.
    """

    def __call__(self):
        self.ensure_profile_installed('profile-ftw.simplelayout:lib')
        self.install_upgrade_profile()
