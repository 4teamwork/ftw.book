from Products.TinyMCE.browser.browser import TinyMCEBrowserView
import json


class BookTextBlockTinyMCEBrowserView(TinyMCEBrowserView):

    def jsonConfiguration(self, *args, **kwargs):
        """Return a customized configuration in JSON"""
        config = super(BookTextBlockTinyMCEBrowserView,
                       self).jsonConfiguration(*args, **kwargs)
        config = json.loads(config)
        config[u'theme_advanced_buttons1'] += (u',tinymce_keyword,'
                                               u'tinymce_footnote,')
        return json.dumps(config)
