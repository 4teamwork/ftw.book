from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.templating import MakoTemplating
import os


class VisualHighlightSubconverter(subconverter.SubConverter, MakoTemplating):
    """Converts span tags with plones "visualHighlight" class to a \hl tag
    (requires soulutf8 package) which highlights the text in the PDF too.
    """

    pattern = r'<span.*?class="[^=]*?visualHighlight[^"]*"[^>]*>(.*?)</span>'
    template_directories = ['latex_packages']

    def __init__(self, *args, **kwargs):
        subconverter.SubConverter.__init__(self, *args, **kwargs)
        MakoTemplating.__init__(self)

    def __call__(self):
        self.register_packages()

        content = self.match.groups()[0]
        latex = r'\hl{%s}' % content
        self.replace(latex)

    def register_packages(self):
        layout = self.converter.converter.layout

        layout.use_package('soulutf8')
        self.add_package('soulutf8.sty')
        self.add_package('infwarerr.sty')
        self.add_package('etexcmds.sty')

    def add_package(self, filename):
        layout = self.converter.converter.layout
        builder = layout.get_builder()

        filepath = os.path.join(builder.build_directory, filename)
        if os.path.exists(filepath):
            return False

        file_ = self.get_raw_template(filename)
        builder.add_file(filename, file_)
