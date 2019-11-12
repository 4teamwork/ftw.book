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
      var scrollTop = $(this).scrollTop();
      if(last_scrollTop_position < scrollTop) {
        update_viewport('down');
        update_navigation_active_state(false);
      } else {
        update_viewport('up');
        update_navigation_active_state(true);
      }

      last_scrollTop_position = scrollTop;
    });

    update_reader_height();
    setTimeout(update_reader_height, 500);

    $(window).resize(update_reader_height);
    initialize_navigation();
    update_navigation_active_state();
  };

  var update_reader_height = function() {
    $('.book-reader > div').height(0);
    var content_div_minheight = $('#content').css('min-height');
    $('#content').css('min-height', '0');
    var last_element_selector = '.bookReaderLastElement, #visual-portal-wrapper > *:not(.visualClear):last, #bottom-actions > *:not(.visualClear):last, footer#portal-footer-wrapper #portal-footer';
    if($(last_element_selector).length === 0) {
      throw 'Could not find last element of page with selector $("' + last_element_selector + '");';
    }

    var $last_element = $(last_element_selector).first();
    $last_element.css('min-height', '0');
    var content_height = $last_element.offset().top + $last_element.height();
    $last_element.css('min-height', null);
    var h = $(window).height() - content_height - 30;
    $('.book-reader > div').height(h);
    $('#content').css('min-height', content_div_minheight);
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
      url = get_baseurl() + 'book_reader_view/render_next';
      data = {after_uid: last_bottom_uid,
              loaded_blocks: get_loaded_uids()};

    } else if (direction == 'up') {
      url = get_baseurl() + 'book_reader_view/render_previous';
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

                  parse_and_register_blocks(data.data).each(function() {
                    $(this).insertAfter(after_elm);
                    after_elm = $(this);
                  });
                }
                request_reload_down = false;

              } else if (direction == 'up') {
                if (!data.data || data.data.length === 0) {
                  top_reached = true;

                } else {
                  last_top_uid = data.first_uid;

                  var $reader = $('.book-reader-content');
                  var posFromBottom = (
                      $reader[0].scrollHeight - $reader.scrollTop());

                  parse_and_register_blocks(data.data).each(function() {
                    $(this).insertBefore(loaded_blocks[data.insert_before]);
                  });

                  $reader.scrollTop(($reader[0].scrollHeight -
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

    var scrollTop = $content.scrollTop();
    var scrollHeight = $content[0].scrollHeight;
    var clientHeight = $content[0].clientHeight;

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
      if (!$(this).data('uid') && $(this).attr('data-uid')) {
        /* Fix data for older jquery versions */
        $(this).data('uid', $(this).attr('data-uid'));
      }
      navigation_map[$(this).data('uid')] = $(this);

      $(this).click(function(e) {
        e.preventDefault();
        goto_block($(this).data('uid'), $(this).attr('href'));
      });
    });
  };

  var navigation_last_update_scrollTop = -1;
  var update_navigation_active_state = function(scrollup) {
    /* Find any element in the middle of the content div at the top. */
    var $content = $('.book-reader-content');
    if($content.scrollTop() === navigation_last_update_scrollTop) {
      return;
    }

    var $link;
    if($content.scrollTop() === 0) {
      /* take first element in navigation if scrolled to top */
      $link = $('div.book-reader-navigation a:first');

    } else {
      var top = Math.round($content.offset().top + 5);
      var left = Math.round($content.offset().left + ($content.width() * 0.5));
      var elm = document.elementFromPoint(left, top);
      if (elm === null) {
        /* In internet explorer this sometimes fails while scrolling, so
           we need to wait */
        setTimeout(function() {update_navigation_active_state(scrollup);}, 2);
        return;
      }
      navigation_last_update_scrollTop = $content.scrollTop();

      var selector = 'span.book-reader-block:first';
      var $block;

      /* Traverse up from the elevent and search the first span.book-reader-block */
      if ($(elm).is(selector)) {
        $block = $(elm);
      } else {
        $block = $(elm).parents(selector);
      }

      /* We need to find a span.book-reader-block which is in the navigation. Check
         the previous siblings until we find one. */
      for(var i=0; i<999999; i++) {
        if (i === 200) {
          /* return the function, not only break the loop */
          return;
        } else if (!$block || $block.length === 0) {
          return;
        } else if ($block.data('READER-UID') &&
                   navigation_map[$block.data('READER-UID')]) {
          break;
        } else {
          $block = $block.prev(selector);
        }
      }

      $link = navigation_map[$block.data('READER-UID')];
    }

    /* Set active class properly */
    $('.book-reader-navigation a.active').removeClass('active');
    $link.addClass('active');

    /* Only scroll if there are no pending effects. */
    if ($('div.book-reader-navigation').queue().length === 0) {
      /* Check if the active link is visible, otherwise scroll to it. */
      var link_top = $link.offset().top;
      var link_bottom = link_top + $link.height();
      var navscroll_top = $('div.book-reader-navigation').offset().top;
      var navscroll_bottom = navscroll_top + $('div.book-reader-navigation').height();
      var link_visible = (link_top > navscroll_top && link_bottom < navscroll_bottom);

      if (!link_visible) {
        var offset = 50;
        var scrollto = ($('div.book-reader-navigation').scrollTop() -
                        navscroll_top + link_top - offset);
        if (scrollup) {
          scrollto -= $('div.book-reader-navigation').height() - (2 * offset);
        }

        $('div.book-reader-navigation').animate({
          scrollTop: scrollto
        }, 500);
      }
    }
  };

  function get_baseurl() {
    var baseurl = $('head base').attr('href');
    if (!baseurl) {
      baseurl = $('body').data('base-url');
    }

    if(baseurl.substr(baseurl.length-1, 1) != '/') {
      baseurl += '/';
    }
    return baseurl;
  }

  /* stay in reader when clicking on book internal links */
  $('a.book-internal').on('click', function(e) {
    e.preventDefault();
    goto_block($(this).data('uid'), $(this).attr('href'));
  });

  $(document).ready(function(){
    init_reader_view();
  });
})(jQuery);
