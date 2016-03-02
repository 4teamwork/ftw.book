/**
 * TinyMCE keyword plugin
 */

(function() {
  tinyMCE.addI18n('en.keyword',{
    title : 'Keyword'
  });

  tinyMCE.addI18n('de.keyword',{
    title : 'Stichwort'
  });


  tinymce.create('tinymce.plugins.Keyword', {
    init : function(ed, url) {
      this.editor = ed;

      // Register commands
      ed.addCommand('mceKeyword', function() {
        var se = ed.selection;

        var span = ed.dom.getParent(ed.selection.getNode(), 'span');
        var within_keyword = (span && span.getAttribute(
            'class') && span.getAttribute('class').indexOf('keyword') > -1);
        if (se.isCollapsed() && !within_keyword) {
          return;
        }

        ed.windowManager.open({
          file : url + '/keyword.htm',
          width : 400 + parseInt(
              ed.getLang('advanced.anchor_delta_width', 0), 10),
          height : 90 + parseInt(
              ed.getLang('advanced.anchor_delta_height', 0), 10),
          inline : 1
        }, {
          plugin_url : url
        });
      });

      // Register buttons
      ed.addButton('tinymce_keyword', {
        title : 'keyword.title',
        cmd : 'mceKeyword',
        img : ''
      });

      ed.onNodeChange.add(function(ed, cm, n, co) {
        cm.setDisabled('tinymce_keyword', co);
        cm.setActive('tinymce_keyword', false);

        var span = ed.dom.getParent(ed.selection.getNode(), 'span');
        if (span) {
          var enabled = (span.getAttribute('class') &&
                         span.getAttribute('class').indexOf('keyword') > -1);
          if (!enabled) return;

          cm.setActive('tinymce_keyword', true);
          cm.setDisabled('tinymce_keyword', false);
        }
      });
    },

    getInfo : function() {
      return {
        longname : 'keyword plugin',
        author : 'jone',
        authorurl : 'http://www.4teamwork.ch/',
        version : tinymce.majorVersion + "." + tinymce.minorVersion
      };
    }
  });

  // Register plugin
  tinymce.PluginManager.add('tinymce_keyword', tinymce.plugins.Keyword);
})();
