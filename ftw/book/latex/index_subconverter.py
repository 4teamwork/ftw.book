from ftw.pdfgenerator.html2latex import subconverter


class IndexSubconverter(subconverter.SubConverter):
    """The IndexSubconverter inserts a LaTeX ``\index{}`` command
    for each index entry.

    Supported formats:

    - <span title="Word">Word</span>
    - <keyword title="Word" />
    """

    pattern = r'<keyword [^>]*title="([^"]*)"[^/]*/>'

    def __call__(self):
        title, = self.match.groups()
        text = self.converter.quoted_umlauts(title)
        self.replace_and_lock(r'\index{%s}' % text)
