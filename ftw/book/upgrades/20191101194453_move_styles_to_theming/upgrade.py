from ftw.upgrade import UpgradeStep


class MoveStylesToTheming(UpgradeStep):
    """Move styles to theming.
    """

    def __call__(self):
        self.install_upgrade_profile()
