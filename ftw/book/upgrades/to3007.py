from ftw.upgrade import UpgradeStep


class MigrateRemark(UpgradeStep):

    def __call__(self):
        from ftw.book.content.remark import Remark
        for obj in self.objects({'portal_type': 'Remark'},
                                'Migrate Remark class'):

            # The Remark class stays the same but subclasses
            # the ftw.contentpage TextBlock class now.
            # For having up to date objects we mainly recalculate
            # the provided interfaces (using self.migrate_class) and
            # reindex the corresponding index.
            self.migrate_class(obj, Remark)
            obj.reindexObject(idxs=['object_provides'])
