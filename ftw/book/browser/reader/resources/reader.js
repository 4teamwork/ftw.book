var init_reader_view;

(function($) {

  var last_top_uid = '';
  var top_reached = false;
  var last_bottom_uid = '';
  var bottom_reached = false;
  var last_scrollTop_position = 0;
  var loaded_blocks = {};

  init_reader_view = function (options) {
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

  var get_loaded_uids = function() {
    var loaded_uids = [];
    for(var uid in loaded_blocks) {
      loaded_uids.push(uid);
    }
    return loaded_uids;
  };

  var load_data = function(direction, callback) {
    var url = '';
    var data = {};

    if (direction == 'down') {
      url = 'book_reader_view/render_next';
      data = {after_uid: last_bottom_uid,
              loaded_blocks: get_loaded_uids()};
    } else if (direction == 'up') {
      url = 'book_reader_view/render_previous';
      data = {before_uid: last_top_uid,
              loaded_blocks: get_loaded_uids()};
    }

    $.ajax({url: url,
            data: data,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
              if (direction == 'down') {
                if (!data.data || data.data.length === 0) {
                  bottom_reached = true;

                } else {
                  last_bottom_uid = data.last_uid;
                  var after_elm;

                  if (data.insert_after == 'TOP') {
                    last_top_uid = data.first_uid;
                    after_elm = $('.book-reader-top-marker');
                  } else {
                    after_elm = loaded_blocks[data.insert_after];
                  }

                  parse_and_register_blocks(data.data).insertAfter(
                    after_elm);
                }

              } else if (direction == 'up') {
                if (!data.data || data.data.length === 0) {
                  top_reached = true;

                } else {
                  last_top_uid = data.first_uid;

                  var $reader = $('.book-reader-content');
                  var posFromBottom = (
                    $reader.attr('scrollHeight') - $reader.attr(
                      'scrollTop'));

                  parse_and_register_blocks(data.data).insertBefore(
                    loaded_blocks[data.insert_before]);

                  $reader.attr('scrollTop', ($reader.attr('scrollHeight') -
                                             posFromBottom));
                }
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
      if (bottom_reached) {
        return false;
      }

      var current_bottom = scrollTop + clientHeight;
      var preload_until = current_bottom + (
        clientHeight * viewport_preload_factor);
      var loaded_until = scrollHeight;

      return loaded_until <= preload_until;

    } else if (direction == 'up') {
      if (top_reached) {
        return false;
      }

      return (clientHeight * viewport_preload_factor) > scrollTop;
    }

  };

})(jQuery);
