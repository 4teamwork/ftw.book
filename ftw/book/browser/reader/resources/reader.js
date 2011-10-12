var init_reader_view;

(function($) {

  var next_uid = null;
  var prev_uid = null;
  var last_scrollTop_position = 0;
  var loaded_blocks = {};

  init_reader_view = function (options) {
    next_uid = options['next_uid'];
    prev_uid = options['prev_uid'];
    update_viewport('down', function() {
      update_viewport('up');});

    $('.book-reader-content').bind('scroll', function(e) {
      var scrollTop = $(this).attr('scrollTop');
      if(last_scrollTop_position < scrollTop) {
        update_viewport('down');
      } else {
        update_viewport('up');
      }

      last_scrollTop_position = scrollTop;
    });

    update_reader_height();

    $(window).resize(update_reader_height);
  };

  var update_reader_height = function() {
    var h = $(window).height() - ($('html').height() - $('.book-reader').height());
    $('.book-reader > div').height(h);
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

                parse_and_register_blocks(data.data).insertBefore(
                  $('.book-reader-bottom-marker'));
              } else if (direction == 'up') {
                prev_uid = data.previous_uid;

                var $reader = $('.book-reader-content');
                var posFromBottom = (
                  $reader.attr('scrollHeight') - $reader.attr('scrollTop'));

                parse_and_register_blocks(data.data).insertAfter(
                  $('.book-reader-top-marker'));

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

  var parse_and_register_blocks = function(data) {
    var elements = $('');

    $(data).each(function() {
      var uid = this[0];
      var elm = $('<span class="book-reader-block">' + this[1] + '</span>');
      elm.data('READER-UID', uid);
      elements = elements.add(elm);
      loaded_blocks[uid] = elm;
    });

    return elements;
  };

  var is_loading_required = function(direction) {
    var $content = $('.book-reader-content');
    var viewport_preload_factor = 1;

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
