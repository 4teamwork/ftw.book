/**
 * TinyMCE footnote plugin
 */

(function() {
  tinyMCE.addI18n('en.footnote',{
    title : 'Footnote'
  });

  tinyMCE.addI18n('de.footnote',{
    title : 'Fussnote'
  });


  tinymce.create('tinymce.plugins.Footnote', {
    init : function(ed, url) {
      this.editor = ed;

      // Register commands
      ed.addCommand('mceFootnote', function() {
        var se = ed.selection;

        ed.windowManager.open({
          file : url + '/footnote.htm',
          width : 600 + parseInt(
              ed.getLang('advanced.anchor_delta_width', 0), 10),
          height : 190 + parseInt(
              ed.getLang('advanced.anchor_delta_height', 0), 10),
          inline : 1
        }, {
          plugin_url : url
        });
      });

      // Register buttons
      ed.addButton('tinymce_footnote', {
        title : 'footnote.title',
        cmd : 'mceFootnote',
        img : ''
      });

      ed.onNodeChange.add(function(ed, cm, n, cursor_only) {
        cm.setDisabled('tinymce_footnote', cursor_only);
        cm.setActive('tinymce_footnote', false);

        var span = ed.dom.getParent(ed.selection.getNode(), 'span.footnote');
        if (span) {
          cm.setActive('tinymce_footnote', true);
          cm.setDisabled('tinymce_footnote', false);
        }
      });
    },

    getInfo : function() {
      return {
        longname : 'footnote plugin',
        author : 'shylux',
        authorurl : 'http://www.4teamwork.ch/',
        version : tinymce.majorVersion + "." + tinymce.minorVersion
      };
    }
  });

  // Register plugin
  tinymce.PluginManager.add('tinymce_footnote', tinymce.plugins.Footnote);
})();
