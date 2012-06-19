import sys


class Tableprinter(object):
    """Simple class to print an ascii table."""

    def __init__(self, widths, separator=' '):
        """Constructor for table printer.

        Keyword arguments:
        widths -- tuple containing the width for each column
        separator -- the column separator (default ' ')

        """
        self.widths = widths
        self.separator = separator

    def print_line(self, items):
        """Print data line.

        Keyword arguments:
        items -- tuple containing row data

        """
        pairs = zip(items, self.widths)
        for item, width in pairs:
            sys.stdout.write(item.ljust(width).encode(sys.stdout.encoding, 'replace') + self.separator)
        sys.stdout.write('\n')

    def print_separator(self, char='-'):
        """Print separator line.

        Keyword arguments:
        char -- character to use for printing the separator

        """
        width = sum(self.widths) + len(self.separator) * len(self.widths)
        print char * width
