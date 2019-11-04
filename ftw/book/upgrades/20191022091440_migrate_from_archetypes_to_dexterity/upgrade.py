from ftw.book.migration import MigrationUpgradeStepMixin
from ftw.upgrade import UpgradeStep
import os


class MigrateFromArchetypesToDexterity(UpgradeStep, MigrationUpgradeStepMixin):
    """Migrate from Archetypes to Dexterity.
    """

    def __call__(self):
        if os.environ.get('FTW_BOOK_SKIP_DEXTERITY_MIGRATION', '').lower() == 'true':
            return
        self.install_upgrade_profile()
        self.migrate_all_book_types()
