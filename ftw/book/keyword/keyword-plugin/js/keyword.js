
var KeywordDialog = {
  init : function(mcePopup) {
    var action, elm, f = document.forms[0];

    this.editor = tinyMCEPopup.editor;

    ed = this.editor;
    elm = ed.dom.getParent(ed.selection.getNode(), 'span');
    v = ed.dom.getAttrib(elm, 'title');

    if (v) {
      this.action = 'update';
      f.keywordName.value = v;
    } else {
      f.keywordName.value = ed.selection.getContent({format : 'text'});
    }

    f.insert.value = ed.getLang(elm ? 'update' : 'insert');
  },

  update : function() {
    var ed = this.editor, elm, keyword = document.forms[0].keywordName.value;

    tinyMCEPopup.restoreSelection;

    elm = ed.dom.getParent(ed.selection.getNode(), 'span');

    /* if no keyword text is defined and there was / is a
       keyword span, remove the span */
    if (!keyword) {
      if (elm) {
        b = ed.selection.getBookmark();
        ed.dom.remove(elm, 1);
        ed.selection.moveToBookmark(b);
        tinyMCEPopup.execCommand("mceEndUndoLevel");
        tinyMCEPopup.close();
        return;
      }
    }

    if (elm) {
      /* update the keyword title */
      elm.title = keyword;

      /* add the keyword class if missing. this happens when there
         already was a span tag */
      if (!elm.getAttribute('class')) {
        elm.setAttribute('class', 'keyword');
      } else if (elm.getAttribute('keyword') == -1) {
        elm.setAttribute('class', elm.getAttribute('class') + ' keyword');
      }

    } else {
      /* create a new span tag around the selected text */
      ed.execCommand('mceInsertContent', 0,
                     ' ' + ed.dom.createHTML(
                         'span', {title: keyword,
                                  'class' : 'keyword'},
                         ed.selection.getContent({format : 'text'})));
    }

    tinyMCEPopup.close();
  }
};

tinyMCEPopup.onInit.add(KeywordDialog.init, KeywordDialog);
