!function(){function e(){$('#form-widgets-column_properties input[name^="form.widgets.column_properties"][name$=".widgets.column_title"]').each(function(){var e=$(this);e.parent().append($("<span>"+e.attr("value")+"</span>")),e.remove()}),$(n).each(function(e){var n=$(this);$("#form-widgets-data tr > *:nth-child("+(e+1)+")").toggle(n.is(":checked"))})}var n='#form-widgets-column_properties input[name^="form.widgets.column_properties"][name$=".widgets.active:list"]';window.book_table_activate_data_columns=e,$(document).on("onLoad OverlayContentReloaded",".overlay",function(){"undefined"!=typeof dataGridField2Functions&&dataGridField2Functions.init&&(dataGridField2Functions.init(),e())}),$(document).on("change",n,e),$(document).ready(e)}(),define("table",function(){}),require(["table"],function(e){}),define("main",function(){});