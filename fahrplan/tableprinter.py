# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import logging

import six


class Tableprinter(object):
    """Simple class to print an ascii table. Expects unicode data."""

    def __init__(self, widths, separator=' '):
        """Constructor for table printer.

        Keyword arguments:
        widths -- tuple containing the width for each column
        separator -- the column separator (default ' ')

        """
        self.widths = widths
        self.separator = separator
        self.encoding = sys.stdout.encoding or 'utf-8'
        logging.debug('Using output encoding %s' % self.encoding)

    def print_line(self, items):
        """Print data line.

        Keyword arguments:
        items -- tuple containing row data

        """
        pairs = zip(items, self.widths)
        for item, width in pairs:
            out = item.ljust(width) + self.separator
            if not six.PY3:
                out = out.encode(self.encoding, 'replace')
            print(out, end='')
        print()

    def print_separator(self, char='-'):
        """Print separator line.

        Keyword arguments:
        char -- character to use for printing the separator

        """
        width = sum(self.widths) + len(self.separator) * len(self.widths)
        print(char * width)
