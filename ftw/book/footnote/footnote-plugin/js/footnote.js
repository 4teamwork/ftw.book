
var FootnoteDialog = {
  init : function(mcePopup) {
    var action;
    var form = document.forms[0];

    this.editor = tinyMCEPopup.editor;

    ed = this.editor;
    var elm = ed.dom.getParent(ed.selection.getNode(), 'span.footnote');
    var footnoteText = ed.dom.getAttrib(elm, 'data-footnote');

    if (footnoteText) {
      this.action = 'update';
      form.footnoteText.value = footnoteText;
    }

    form.insert.value = ed.getLang(elm ? 'update' : 'insert');
  },

  update : function() {
    var ed = this.editor;
    var footnoteText = document.forms[0].footnoteText.value;

    tinyMCEPopup.restoreSelection;

    elm = ed.dom.getParent(ed.selection.getNode(), 'span.footnote');

    /* if no footnote text is defined and there was / is a
       footnote span, remove the span */
    if (!footnoteText) {
      if (elm) {
        bookmark = ed.selection.getBookmark();
        ed.dom.remove(elm.getElementsByClassName('footnote-info'), false);
        ed.dom.remove(elm, 1);
        ed.selection.moveToBookmark(bookmark);
        tinyMCEPopup.execCommand("mceEndUndoLevel");
        tinyMCEPopup.close();
        return;
      }
    }

    if (elm) {
      /* update the footnote data */
      elm.setAttribute('data-footnote', footnoteText);
    } else {
      /* create a new span tag around the selected text and insert footnote*/
      ed.execCommand('mceInsertContent', 0,
                     ' ' + ed.dom.createHTML(
                         'span', {'data-footnote': footnoteText,
                                  'class': 'footnote'},
                         ed.selection.getContent({format: 'text'})));
    }

    tinyMCEPopup.close();
  }
};

tinyMCEPopup.onInit.add(FootnoteDialog.init, FootnoteDialog);
