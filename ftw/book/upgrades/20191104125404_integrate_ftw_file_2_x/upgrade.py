from ftw.upgrade import UpgradeStep


class IntegrateFtwFile2X(UpgradeStep):
    """Integrate ftw.file 2.x.
    """

    def __call__(self):
        self.ensure_profile_installed('ftw.file:default')
        self.install_upgrade_profile()
