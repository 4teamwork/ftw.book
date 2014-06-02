from Products.TinyMCE.browser.browser import TinyMCEBrowserView
import json


class BookTextBlockTinyMCEBrowserView(TinyMCEBrowserView):

    def jsonConfiguration(self, *args, **kwargs):
        """Return a customized configuration in JSON"""
        config = super(BookTextBlockTinyMCEBrowserView,
                       self).jsonConfiguration(*args, **kwargs)
        config = json.loads(config)
        if u'theme_advanced_buttons1' in config:
            # Plone >= 4.3
            config[u'theme_advanced_buttons1'] += u',tinymce_keyword'
        else:
            # Plone <= 4.2
            config[u'buttons'].append(u'tinymce_keyword')
        return json.dumps(config)
