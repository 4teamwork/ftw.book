(function($) {

  var last_top_uid = '';
  var top_reached = false;
  var last_bottom_uid = '';
  var bottom_reached = false;
  var last_scrollTop_position = 0;
  var loaded_blocks = {};
  var navigation_map = {};

  /* queueing helpers */
  var loading = false;
  var request_reload_up = false;
  var request_reload_down = false;

  var init_reader_view = function () {
    update_viewport('down');
    update_viewport('up');

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
    initialize_navigation();
  };

  var update_reader_height = function() {
    $('.book-reader > div').height(0);
    var $last_element = $('#visual-portal-wrapper > *:last');
    var content_height = $last_element.offset().top + $last_element.height();
    var h = $(window).height() - content_height - 30;
    $('.book-reader > div').height(h);
  };

  var update_viewport = function(direction) {
    if(direction == 'up') {
      request_reload_up = true;
    } else {
      request_reload_down = true;
    }

    if (!loading) {
      trigger_load_data();
    }
  };

  var get_loaded_uids = function() {
    var loaded_uids = [];
    for(var uid in loaded_blocks) {
      loaded_uids.push(uid);
    }
    return loaded_uids;
  };

  var trigger_load_data = function() {
    if (!loading) {
      if (request_reload_down) {
        if (is_loading_required('down')) {
          load_data('down');
        } else {
          request_reload_down = false;
          trigger_load_data();
        }

      } else if (request_reload_up) {
        if (is_loading_required('up')) {
          load_data('up');
        } else {
          request_reload_up = false;
        }
      }
    }
  };

  var load_data = function(direction, callback) {
    loading = true;
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
                request_reload_down = false;

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
                request_reload_up = false;
              }

              if (is_loading_required(direction)) {
                update_viewport(direction);
              }

              loading = false;
              trigger_load_data();

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
    var viewport_preload_factor = 2;

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

  var goto_block = function(uid, url) {
    if (loaded_blocks[uid]) {
      var pos = $('.book-reader-content').scrollTop();
      pos += loaded_blocks[uid].position().top;
      pos -= 30;
      $('.book-reader-content').scrollTop(pos);

    } else {
      location.href = url + '/@@book_reader_view';
    }
  };

  var initialize_navigation = function() {
    $('div.book-reader-navigation a').each(function() {
      navigation_map[$(this).data('uid')] = $(this);

      $(this).click(function(e) {
        e.preventDefault();
        goto_block($(this).data('uid'), $(this).attr('href'));
      });
    });
  };

  $('div.table-of-contents a').live('click', function(e) {
    e.preventDefault();
    goto_block($(this).data('uid'), $(this).attr('href'));
  });


  $(document).ready(function(){
    init_reader_view();
  });
})(jQuery);
