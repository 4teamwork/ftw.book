class ColumnWidthsCalculator(object):
    """ Object to calculate table column widths
    """

    MAX_WIDTH = 100  # The sum of all columnwidths

    def __call__(self, widths):
        """ Start calculating the widths with two different algorithms
        """

        if not widths:
            return widths

        # List of available algorithms
        queue = [
            self.validate_widths,
            self.to_float,
            self.calculate_in_percent,
            self.calculate_in_ratio,
            self.calculate_propotions,
            self.to_int,
            self.resolve_rounding_problems,
            ]

        # Start calculating the withs
        for job in queue:
            widths = job(widths)

        return widths

    def calculate_in_percent(self, widths):
        """ Calculate the width for the columns in percent.
        The user can define his own widths. We have to validate that and
        calculate not setted widths

        This algoritm has no effect if the sum of the user defined widths
        is more than MAX_WIDTH.
        """
        remaining_width = self._get_remaining_width(widths)
        widthless_columns = self._num_widthless_columns(widths)

        # The user has set the width correctly or he made calculation
        # errors that we can't split the remaining width to the widthless
        # columns
        if (remaining_width == 0 and widthless_columns == 0) or \
            remaining_width < widthless_columns:

            pass

        # If the user has set no width so we split the maximum width to the
        # number of columns
        elif widthless_columns == len(widths):
            widths = self._set_column_widths(
                widths, (self.MAX_WIDTH / len(widths)))

        # The user set the width correctly but not for every row
        elif widthless_columns:
            widths = self._set_column_widths(
                widths, remaining_width / widthless_columns, True, 0)

        return widths

    def calculate_in_ratio(self, widths):
        """ Calculate the width for the columns in ratio.
        The user can define his own widths. We have to validate that and
        calculate not setted widths
        """
        widthless_columns = self._num_widthless_columns(widths)
        given_width = self._get_given_width(widths)

        # We set the widthless columns with the average of the widths of
        # the other columns
        widths = self._set_column_widths(
            widths,
            given_width / (len(widths) - widthless_columns),
            True, 0)

        return widths

    def calculate_propotions(self, widths):
        """ We calculate the proportinoal width for each column
        to the MAX_WIDTH value
        """
        new = []
        for width in widths:
            new.append(self.MAX_WIDTH / self._get_given_width(widths) * width)

        return new

    def resolve_rounding_problems(self, widths):
        """ Because rounding-problems its possible that we get a rest. We add
        the rest on the first elements width
        """
        widths[0] += self.MAX_WIDTH - sum(widths)

        return widths

    def validate_widths(self, widths):
        """ Modify the received widths to get valid value
        """

        for i, width in enumerate(widths):
            if not (isinstance(width, int) or isinstance(width, float)):
                if width is None:
                    width = 0
                try:
                    width = int(width)
                except ValueError:
                    width = 0

            widths[i] = abs(width)

        return widths

    def to_int(self, widths):
        """ Converts all list-elements into ints
        """
        return self._convert_list_elements(widths, int)

    def to_float(self, widths):
        """ Converts all list-elements into floats"
        """
        return self._convert_list_elements(widths, float)

    def _convert_list_elements(self, widths, type_):
        """ Converts the type of list elemenets into the given type_
        """
        return [type_(i) for i in widths]

    def _get_given_width(self, widths):
        """ Return the given width.

        Converts negative widths into positive ones and calculate the
        sum of them.
        """
        return sum([abs(x) for x in widths])

    def _get_remaining_width(self, widths):
        """ Return the remaining width to the given max value
        """
        return self.MAX_WIDTH - self._get_given_width(widths)

    def _num_widthless_columns(self, widths):
        """ Return the number of columns which doesn't define a width
        """
        return len(filter(lambda x: x == 0, widths))

    def _set_column_widths(self, widths, width, width_condition=False, cond=0):
        """ Set the column-widths in the widths
        """
        for i, value in enumerate(widths):
            if not width_condition or value == cond:
                widths[i] = width

        return widths
