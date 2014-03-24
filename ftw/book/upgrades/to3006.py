from ftw.upgrade import UpgradeStep


class MigrateHTMLBlock(UpgradeStep):

    def __call__(self):
        from ftw.book.content.htmlblock import HTMLBlock
        for obj in self.objects({'portal_type': 'HTMLBlock'},
                                'Migrate HTMLBlock class'):

            # The HTMLBlock class stays the same but subclasses
            # the ftw.contentpage TextBlock class now.
            # For having up to date objects we mainly recalculate
            # the provided interfaces (using self.migrate_class) and
            # reindex the corresponding index.
            self.migrate_class(obj, HTMLBlock)
            obj.reindexObject(idxs=['object_provides'])
