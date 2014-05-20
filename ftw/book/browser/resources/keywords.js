jQuery().ready(function($) {

  $('form.keywords select').select2({
    allowClear: true
  }).change(function() {
    var form_params = $('form.keywords').serialize();
    var url = './tabbedview_view-keywords/load?' + form_params;
    $(".keyword-results").load(url);
  });

  $("#keyword").select2({width: "300px", allowClear: true});

});
