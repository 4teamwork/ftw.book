from Products.Archetypes.atapi import registerType
from Products.ATContentTypes.content import folder


class Chapter(folder.ATFolder):
    schema = folder.ATFolder.schema.copy()


registerType(Chapter, 'ftw.book')
