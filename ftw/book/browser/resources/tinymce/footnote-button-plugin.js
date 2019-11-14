(function(tinymce) {
  tinymce.PluginManager.add('footnote', function(editor) {
    editor.addButton('footnote', {
      icon: 'footnote',
      image: '++resource++ftw.book-resources/tinymce/footnote_icon.png',
      onclick: function() {
        var selectionContent = editor.selection.getContent();

        var inputSchema = [
          {
            type: 'textbox', name: 'footnote', label: 'Footnote', multiline: 'true'
          }
        ];

        editor.windowManager.open({
          title: 'Add Footnote',
          body: inputSchema,
          onsubmit: function(e) {
            var text = selectionContent ? selectionContent : e.data.text;
            var button = editor.dom.createFragment('\
              <span class="footnote" data-footnote="' + e.data.footnote + '">' + text + '</span>\
              ');
              editor.selection.setNode(button);
            }
        });
      }
    });

    return {
      getMetadata: function () {
        return  {
          name: "Footnote Button Plugin",
          author: "Busykoala"
        };
      }
    };
  });

})(window.tinymce);
