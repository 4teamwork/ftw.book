from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book.interfaces import IBook
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class IGoToParentPortlet(IPortletDataProvider):
    """Contact portlet schema interface
    """


class Assignment(base.Assignment):
    """Contact portlet assignment
    """
    implements(IGoToParentPortlet)

    @property
    def title(self):
        return "Go To Parent Portlet"


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()


class Renderer(base.Renderer):

    template = ViewPageTemplateFile('gotoparent.pt')

    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.parent_title = None
        self.parent_url = None

    def update(self):
        book = self.get_book()

        if book:
            parent = aq_parent(aq_inner(book))
            self.parent_title = parent.Title()
            self.parent_url = parent.absolute_url()

        return super(Renderer, self).update()

    def render(self):
        if self.parent_title is None:
            return ''

        else:
            return self.template()

    def get_book(self):
        obj = self.context

        while obj is not None:
            if IBook.providedBy(obj):
                return obj

            elif IPloneSiteRoot.providedBy(obj):
                return None

            else:
                obj = aq_parent(aq_inner(obj))

        return None
