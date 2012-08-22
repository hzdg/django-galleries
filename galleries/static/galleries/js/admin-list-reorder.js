// From http://djangosnippets.org/snippets/2057/

// Set this to the name of the column holding the position
var pos_field = "sort_order";

/*jslint browser: true */
(function ($) {
    "use strict";
    $(document).ready(function () {

        // Determine the column number of the position field
        var i, inputs, header, sorted, sorted_col, sort_order,
            pos_col = null,
            cols = $('#result_list tbody tr:first').children();

        for (i = 0; i < cols.length; i += 1) {
            inputs = $(cols[i]).find('input[name*=' + pos_field + ']');

            if (inputs.length > 0) {
                // Found!
                pos_col = i;
                break;
            }
        }

        if (pos_col === null) {
            return;
        }

        // Some visual enhancements
        header = $('#result_list thead tr').children()[pos_col];
        // $(header).hide();
        $(header).css('width', '1em');
        $(header).children('a').text('#');

        // Hide position field
        $('#result_list tbody tr').each(function (index) {
            var label,
                pos_td = $(this).children()[pos_col],
                input = $(pos_td).children('input').first();
            //input.attr('type', 'hidden')
            input.hide();

            label = $('<span class="admin-list-reorder-position-field">' + input.attr('value') + '</span>');
            $(pos_td).append(label);
            // $(pos_td).hide();
        });

        // Determine sorted column and order
        sorted = $('#result_list thead th.sorted');
        sorted_col = $('#result_list thead th').index(sorted);
        sort_order = sorted.hasClass('descending') ? 'desc' : 'asc';

        if (sorted_col !== pos_col) {
            // Sorted column is not position column, bail out
            if (typeof window.console !== 'undefined') {
                window.console.info("Sorted column is not %s, bailing out", pos_field);
            }
            return;
        }

        $('#result_list tbody tr').css('cursor', 'move');

        // Make tbody > tr sortable
        $('#result_list tbody').sortable({
            axis: 'y',
            items: 'tr',
            cursor: 'move',
            update: function (event, ui) {
                var item = ui.item,
                    items = $(this).find('tr').get();

                if (sort_order === 'desc') {
                    // Reverse order
                    items.reverse();
                }

                $(items).each(function (index) {
                    var pos_td = $(this).children()[pos_col],
                        input = $(pos_td).children('input').first(),
                        label = $('.admin-list-reorder-position-field', pos_td).first();

                    input.attr('value', index);
                    label.text(index);
                });

                // Update row classes
                $(this).find('tr').removeClass('row1').removeClass('row2');
                $(this).find('tr:even').addClass('row1');
                $(this).find('tr:odd').addClass('row2');
            }
        });
    });
}(window.jQuery));






// Based on http://djangosnippets.org/snippets/1053/
// FIXME: This will make all models on page with sort_order drag-and-drop.

(function ($) {
    "use strict";
    $(document).ready(function () {

		$(".inline-group").each(function (index, el) {
			var headerColumnIndex, header,
                td = $("td." + pos_field, el).first(),
                columnIndex = td.parent().children().index(td);

			if (columnIndex !== -1) {
				headerColumnIndex = 0;
				$("th", el).each(function (index, el) {
					el = $(el);
					if (headerColumnIndex === columnIndex) {
						header = el;
						return false;
					}
					headerColumnIndex += el.attr('colspan') || 1;
				});

				if (header) {
					$(header).css('width', '1em');
					$(header).text('#');
				}

				$("tbody tr td." + pos_field, el).each(function (index) {
					var input = $(this).children("input").first(),
                        label = $('<span class="admin-list-reorder-position-field">' + input.attr('value') + '</span>');
				    input.hide();
				    $(this).append(label);
				});
			}
		});


        $('div.inline-group').sortable({
            items: 'tr.has_original',
            handle: 'td',
            update: function () {
                $(this).find('tr.has_original').each(function (i) {
                    $(this).find('td.sort_order input').val(i + 1);
					$(this).find('td.sort_order .admin-list-reorder-position-field').text(i + 1);
                    $(this).removeClass('row1').removeClass('row2');
                    $(this).addClass('row' + ((i % 2) + 1));
                });
            }
        });
        $('tr.has_original').css('cursor', 'move');

    });
}(window.jQuery));
