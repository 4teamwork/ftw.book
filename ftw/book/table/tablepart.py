class TablePart(object):
    """ A Tablepart object stores different attributes used to
    create tablerows
    """

    def __init__(
        self,
        rows,
        parent,
        begin_at,
        column_names,
        first_column_a_header,
        border_layout,
    ):

        self.rows = rows
        self.begin_at = begin_at
        self.parent = parent
        self.column_names = column_names
        self.first_column_a_header = first_column_a_header
        self.row_node = None
        self.is_first_cell = False
        self.border_layout = border_layout

    def is_first_column_a_header(self):
        """ Should the first column be a header-row
        """
        return self.first_column_a_header

    def is_cell_header_cell(self):
        """ Are we on the first cell and should the first column be a
        header-row
        """
        if self.is_first_cell and self.first_column_a_header:
            return True
        return False

    def get_row_type(self):
        """ Return the type of the row. Can be tr or th'
        """
        return 'tr'

    def get_cell_type(self):
        """ Type of the cell, Can be td or th...
        """
        if self.is_cell_header_cell():
            return 'th'
        return 'td'

    def set_row_node(self, row):
        """ Set the actual row-node we create cells
        """
        self.row_node = row

    def get_row_node(self):
        """ Get the actual row-node we create cells
        """
        return self.row_node

    def set_is_first_cell(self, is_first_cell):
        """ Set true if we are on the first cell
        """
        self.is_first_cell = is_first_cell

    def get_css(self, css, row_num, col_name):
        """ Return default and additional css classes in a list
        """
        css = css

        if self.border_layout in ['fancy_listing', 'grid']:
            css.append('border-bottom')

        if self.border_layout in ['grid']:
            css.append('border-top')
            css.append('border-left')
            css.append('border-right')

        css = self.get_additional_css(css, row_num, col_name)
        css = self.cleanup_css(css)

        return css

    def get_additional_attrs(self, row_num, col_name):
        """ Return additional attrs
        """
        return {}

    def get_additional_css(self, css, row_num, col_name):
        """ Get special css classes
        """
        return css

    def wrap_text_in_attr(self, text):
        """ Wrap a text into an attr
        """
        return text

    def cleanup_css(self, css):
        """ Cleanup the given css. Remove double entries and
        different other cleanups
        """

        if 'noborders' in css:
            for css_class in ['border-bottom', 'border-top', 'noborders']:
                if css_class in css:
                    self._remove_css_class(css, css_class)

        if 'scriptsize' in css and 'bold' in css:
            self._remove_css_class(css, 'bold')

        return set(css)

    def _is_last_column(self, col_name):
        """ Ist the given column name the last of all available columns
        """
        return col_name != self.column_names[-1] and True or False

    def _remove_css_class(self, css, css_class):
        """ Try to remove a css class from the given list of css-classes
        """
        try:
            css.remove(css_class)
        except ValueError:
            pass

        return css


class TablePartHeader(TablePart):
    """ Used for the Head
    """

    def __init__(
        self,
        rows,
        parent,
        begin_at,
        column_names,
        first_column_a_header,
        border_layout,
    ):

        super(TablePartHeader, self).__init__(
            rows,
            parent,
            begin_at,
            column_names,
            first_column_a_header,
            border_layout,
        )

    def get_cell_type(self):
        return 'th'

    def get_additional_attrs(self, row_num, col_name):
        attrs = {'align': 'left'}

        if row_num <= 0:
            attrs['id'] = col_name

        return attrs

    def is_last_row(self, row_num):
        """ Is it the last row
        """
        return len(self.rows) <= row_num + 1


class TablePartFooter(TablePart):
    """ Used for the footer
    """

    def __init__(
        self,
        rows,
        parent,
        begin_at,
        column_names,
        first_column_a_header,
        border_layout,
        footer_is_bold,
    ):

        super(TablePartFooter, self).__init__(
            rows,
            parent,
            begin_at,
            column_names,
            first_column_a_header,
            border_layout,
        )

        self.footer_is_bold = footer_is_bold

    def get_css(self, css, row_num, col_name):
        classes = super(TablePartFooter, self).get_css(css, row_num, col_name)
        if self.footer_is_bold and 'bold' not in classes:
            classes.add('bold')
        return classes


class TablePartBody(TablePart):
    """ Used for the Body
    """

    def get_additional_attrs(self, row_num, col_name):
        attrs = {}

        if self.is_cell_header_cell():
            attrs = {'id': 'row%i' % row_num}
        elif self.is_first_column_a_header():
            attrs = {'headers': '%s row%i' % (col_name, row_num)}
        else:
            attrs = {'headers': '%s' % col_name}

        return attrs
