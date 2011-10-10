var init_reader_view;

(function($) {

  var next_uid = null;
  var prev_uid = null;
  var last_scrollTop_position = 0;

  init_reader_view = function (options) {
    next_uid = options['next_uid'];
    prev_uid = options['prev_uid'];
    update_viewport('down', function() {
      update_viewport('up');});

    $('.book-reader').bind('scroll', function(e) {
      var scrollTop = $(this).attr('scrollTop');
      if(last_scrollTop_position < scrollTop) {
        update_viewport('down');
      } else {
        update_viewport('up');
      }

      last_scrollTop_position = scrollTop;
    });
  };

  var update_viewport = function(direction, callback) {
    if (is_loading_required(direction)) {
      load_data(direction, callback);
    }
  };

  var load_data = function(direction, callback) {
    var url = '';
    var data = {};

    if (direction == 'down') {
      url = 'book_reader_view/render_next';
      data = {next_uid: next_uid};
    } else if (direction == 'up') {
      url = 'book_reader_view/render_previous';
      data = {previous_uid: prev_uid};
    }

    $.ajax({url: url,
            data: data,
            dataType: 'json',
            success: function(data) {
              if (direction == 'down') {
                next_uid = data.next_uid;

                $(data.html).insertBefore(
                  $('.book-reader-bottom-marker'));
              } else if (direction == 'up') {
                prev_uid = data.previous_uid;

                var $reader = $('.book-reader');
                var posFromBottom = (
                  $reader.attr('scrollHeight') - $reader.attr('scrollTop'));

                var content = $(data.html);
                content.insertAfter($('.book-reader-top-marker'));

                $reader.attr('scrollTop', ($reader.attr('scrollHeight') -
                                           posFromBottom));
              }

              if (is_loading_required(direction)) {
                update_viewport(direction, callback);
              } else if(callback) {
                callback();
              }

            }});
  };

  var is_loading_required = function(direction) {
    var $content = $('.book-reader');
    var viewport_preload_factor = 0.5;

    var scrollTop = $content.attr('scrollTop');
    var scrollHeight = $content.attr('scrollHeight');
    var clientHeight = $content.attr('clientHeight');

    if (direction == 'down') {
      if (next_uid === null) {
        return false;
      }

      var current_bottom = scrollTop + clientHeight;
      var preload_until = current_bottom + (
        clientHeight * viewport_preload_factor);
      var loaded_until = scrollHeight;

      return loaded_until <= preload_until;

    } else if (direction == 'up') {
      if (prev_uid === null) {
        return false;
      }

      return (clientHeight * viewport_preload_factor) > scrollTop;
    }

  };

})(jQuery);
