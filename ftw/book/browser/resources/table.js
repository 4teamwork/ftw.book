(function(){

  var active_checkboxes_selector = '#form-widgets-column_properties input[name^="form.widgets.column_properties"][name$=".widgets.active:list"]';

  function activate_data_columns() {
    $('#form-widgets-column_properties input[name^="form.widgets.column_properties"][name$=".widgets.column_title"]').each(function() {
      var column_title_input = $(this);
      column_title_input.parent().
            append($('<span>' + column_title_input.attr('value') + '</span>'));
      column_title_input.remove();
    });

    $(active_checkboxes_selector).each(function(index) {
      var checkbox = $(this);
      $('#form-widgets-data tr > *:nth-child(' + (index + 1) + ')').toggle(
            checkbox.is(':checked'));
    });
  }
  window.book_table_activate_data_columns = activate_data_columns;

  $(document).on('onLoad OverlayContentReloaded', '.overlay', function(){
    if (typeof dataGridField2Functions !== 'undefined' && dataGridField2Functions.init) {
      dataGridField2Functions.init();
      activate_data_columns();
    }
  });

  $(document).on('change', active_checkboxes_selector, activate_data_columns);
  $(document).ready(activate_data_columns);

})();
