from ftw.book.interfaces import IChapter
from ftw.book.toc import TableOfContents
from ftw.simplelayout.browser.simplelayout import SimplelayoutView
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISimplelayoutContainerConfig)
@adapter(IChapter, Interface)
class ChapterConfigAdapter(object):

    def __init__(self, context, request):
        pass

    def __call__(self, settings):
        settings['layouts'] = []

    def default_page_layout(self):
        return {'default': [{"cols": [{"blocks": []}]}]}


class ChapterSimplelayoutView(SimplelayoutView):
    template = ViewPageTemplateFile('templates/chapter_simplelayout.pt')

    def heading(self):
        toc = TableOfContents()
        return toc.html_heading(self.context,
                                classes=['documentFirstHeading'],
                                tagname='h1',
                                prepend_html_headings=True)
