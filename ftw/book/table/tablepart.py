class TablePart(object):
    """ A Tablepart object to stores different attributes used to
    create tablerows
    """

    def __init__(
        self,
        rows,
        parent,
        begin_at,
        active_column_names,
        first_column_a_header,
    ):

        self.rows = rows
        self.begin_at = begin_at
        self.parent = parent
        self.active_column_names = active_column_names
        self.first_column_a_header = first_column_a_header
        self.row_node = None
        self.is_first_cell = False

    def get_begin_at(self):
        """ We have a set of rows. Our part begins perhaps at row 3
        """
        return self.begin_at

    def get_rows(self):
        """ List of datagrid-rows
        """
        return self.rows

    def get_parent(self):
        """ The parent dom-object. Can be a tbody or thead...
        """
        return self.parent

    def get_column_names(self):
        """ Names of available columns
        """
        return self.active_column_names

    def is_first_column_a_header(self):
        """ Should the first column be a header-row
        """
        return self.first_column_a_header

    def is_cell_header_cell(self):
        """ Are we on the first cell and has should the first column be a
        header-row
        """
        if self.is_first_cell and self.first_column_a_header:
            return True
        return False

    def get_cell_type(self):
        """ Type of the cell, Can be td or tr...
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

    def get_is_first_cell(self):
        """ Return true if we are on the first cell
        """
        self.is_first_cell

    def get_part(self):
        """ Return the part of the tablepart. Can be footer or body...
        """
        return ''

    def set_css(self, css):
        self.css = css

    def get_css(self):
        return self.css

class TablePartFooter(TablePart):
    """ Used for the footer
    """

    def get_part(self):
        """ Return the part of the tablepart. Can be footer or body...
        """
        return 'foot'

class TablePartBody(TablePart):
    """ Used for the Body
    """

    def get_part(self):
        """ Return the part of the tablepart. Can be footer or body...
        """
        return 'body'
