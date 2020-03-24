(function(tinymce) {
  tinymce.addI18n('de',{
    "Keyword": "Stichwort",
    "Add Keyword": "Stichwort hinzuf\u00fcgen"
  });
  tinymce.PluginManager.add('keyword', function(editor) {
    editor.addButton('keyword', {
      icon: 'keyword',
      image: '++resource++ftw.book-resources/tinymce/keyword_icon.png',
      onclick: function() {
        var span = editor.dom.getParent(editor.selection.getNode(), 'span');
        var within_keyword = span && span.getAttribute('class') && span.getAttribute('class').indexOf('keyword') > -1;
        var selectionContent = editor.selection.getContent();
        var title = within_keyword ? span.getAttribute('title') : selectionContent;

        var inputSchema = [
          {
            type: 'textbox', name: 'keyword', label: 'Keyword', value: title
          }
        ];

        editor.windowManager.open({
          title: 'Add Keyword',
          body: inputSchema,
          onsubmit: function(e) {
            var text = selectionContent ? selectionContent : e.data.text;
            if (within_keyword) {
              span.title = e.data.keyword
            }
            else {
              var button = editor.dom.createFragment('\
                <span class="keyword" title="' + e.data.keyword + '">' + text + '</span>\
                ');
              editor.selection.setNode(button);
            }
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
