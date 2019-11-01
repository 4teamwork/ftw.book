(function(tinymce) {
  tinymce.PluginManager.add('keyword', function(editor) {
    editor.addButton('keyword', {
      text: 'Keyword',
      icon: false,
      onclick: function() {
        var selectionContent = editor.selection.getContent();

        var inputSchema = [
          {
            type: 'textbox', name: 'keyword', label: 'Keyword'
          }
        ];

        editor.windowManager.open({
          title: 'Add Keyword',
          body: inputSchema,
          onsubmit: function(e) {
            var text = selectionContent ? selectionContent : e.data.text;
            var button = editor.dom.createFragment('\
              <span class="keyword" title="' + e.data.keyword + '">' + text + '</span>\
              ');
              editor.selection.setNode(button);
            }
        });
      }
    });

    return {
      getMetadata: function () {
        return  {
          name: "Keyword Button Plugin",
          author: "Busykoala"
        };
      }
    };
  });

})(window.tinymce);
