# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import logging

import six


class Tableprinter(object):
    """Simple class to print an ascii table. Expects unicode data."""

    def __init__(self, widths, separator=' '):
        """Constructor for table printer.

        Args:
            widths: Tuple containing the width for each column.
            separator: The column separator (default ' ').

        """
        self.widths = widths
        self.separator = separator
        try:
            self.encoding = sys.stdout.encoding or 'utf-8'
        except AttributeError:
            self.encoding = 'utf-8'
        logging.debug('Using output encoding %s' % self.encoding)

    def print_line(self, items):
        """Print data line.

        Args:
            items: Tuple containing row data.

        """
        pairs = zip(items, self.widths)
        for item, width in pairs:
            out = item.ljust(width) + self.separator
            if not six.PY3:
                out = out.encode(self.encoding, 'replace')
            print(out, end='')
        print()  # newline

    def print_separator(self, char='-', cols=[]):
        """Print separator line.

        Args:
            char: Character to use for printing the separator.
            cols: The 0 based column indexes, where the separator should be
                printed (by default the line is printed across all columns)

        """
        if not cols:
            width = sum(self.widths) + len(self.separator) * len(self.widths)
            print(char * width)
        else:
            for i in range(len(self.widths)):
                symbol = char if i in cols else ' '
                print(symbol * self.widths[i], end='')
                print(self.separator, end='')
            print()  # newline
