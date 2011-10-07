from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements
from ftw.book import _
from ftw.book.interfaces import IBook


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

    def get_parent_link(self):
        context = self.context.aq_inner
        Book = context
        while not IBook.providedBy(Book):
            Book = Book.aq_parent
        parent = Book.aq_parent
        url = parent.absolute_url()
        title = parent.title
        tranlation = _(u'Return to ', default=u'Return to')
        return '<a class="gotoparentlink" href="%s">%s</a>' % (url, tranlation + title)

    render = ViewPageTemplateFile('gotoparent.pt')


