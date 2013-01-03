#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A SBB/CFF/FFS commandline based timetable client.
# Copyright (C) 2012 Danilo Bargen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import json
import logging
from functools import partial

import six
import requests
import dateutil.parser

from . import meta
from .tableprinter import Tableprinter
from .parser import parse_input

__version__ = meta.version

API_URL = 'http://transport.opendata.ch/v1'
ENCODING = sys.stdout.encoding or 'utf-8'


# Helper function to print directly to sys.stderr
perror = partial(print, file=sys.stderr)


def main():

    """1. Parse arguments."""

    def assert_enough_arguments(args):
        if len(args) <= 1:
            perror('Not enough arguments.')
            sys.exit(1)

    assert_enough_arguments(sys.argv)

    tokens = sys.argv[1:]
    if isinstance(tokens[0], six.binary_type):
        tokens = [arg.decode(ENCODING) for arg in tokens]
    while tokens and tokens[0].startswith('-'):
        if tokens[0] in ['-h', '--help']:
            out = ('{meta.title}: {meta.description}\n'.format(meta=meta)
                + '\n'
                + 'Usage:\n'
                + ' {meta.title} [options] arguments\n'.format(meta=meta)
                + '\n'
                + 'Options:\n'
                + ' -v, --version Show version number\n'
                + ' -i, --info    Verbose output\n'
                + ' -d, --debug   Debug output\n'
                + ' -h, --help    Show this help\n'
                + '\n'
                + 'Arguments:\n'
                + ' You can use natural language arguments using the following\n'
                + ' keywords in your desired language:\n'
                + ' en -- from, to, via, departure, arrival\n'
                + ' de -- von, nach, via, ab, an\n'
                + ' fr -- de, à, via, départ, arrivée\n'
                + '\n'
                + ' You can also use natural time specifications in your language, like "now",\n'
                + ' "immediately", "noon" or "midnight".\n'
                + '\n'
                + 'Examples:\n'
                + ' fahrplan from thun to burgdorf\n'
                + ' fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35\n'
                + ' fahrplan de lausanne à vevey arrivée minuit\n'
                + '\n')
            print(out.encode(ENCODING, 'replace'))
            sys.exit(0)
        if tokens[0] in ['-v', '--version']:
            print('{meta.title} {meta.version}'.format(meta=meta))
            sys.exit(0)
        if tokens[0] in ['-i', '--info']:
            logging.basicConfig(level=logging.INFO)
        if tokens[0] in ['-d', '--debug']:
            logging.basicConfig(level=logging.DEBUG)
        del tokens[0]

    assert_enough_arguments(tokens)
    try:
        args, language = parse_input(tokens)
    except ValueError as e:
        perror('Error:', e)
        sys.exit(1)


    """2. Do API request."""

    url = '%s/connections' % API_URL
    try:
        response = requests.get(url, params=args)
    except requests.exceptions.ConnectionError:
        perror('Error: Could not reach network.')
        sys.exit(1)

    logging.debug('Response status: {0!r}'.format(response.status_code))

    if not response.ok:
        verbose_status = requests.status_codes._codes[response.status_code][0]
        perror('Server Error: HTTP %s (%s)' %
                 (response.status_code, verbose_status))
        sys.exit(1)

    try:
        data = json.loads(response.text)
    except ValueError:
        logging.debug('Response status code: {0}'.format(response.status_code))
        logging.debug('Response content: {0!r}'.format(response.content))
        perror('Error: Invalid API response (invalid JSON)')
        sys.exit(1)

    connections = data['connections']

    if not connections:
        msg = 'No connections found from "%s" to "%s".' % \
              (data['from']['name'], data['to']['name'])
        print(msg.encode(ENCODING))
        sys.exit(0)


    """3. Process and output data."""

    table = [parse_connection(c) for c in connections]

    # Define columns
    cols = (
        u'#', u'Station', u'Platform', u'Date', u'Time',
        u'Duration', u'Chg.', u'Travel with', u'Occupancy',
    )

    # Calculate and set column widths
    station_width = len(max([t['station_from'] for t in table] +
                            [t['station_to'] for t in table],
                            key=len))
    travelwith_width = len(max([t['travelwith'] for t in table], key=len))
    widths = (
        2,
        max(station_width, len(cols[1])),  # station
        max(4,  len(cols[2])),   # platform (TODO width)
        max(13, len(cols[3])),   # date
        max(5,  len(cols[4])),   # time
        max(5,  len(cols[5])),   # duration
        max(2,  len(cols[6])),   # changes
        max(travelwith_width, len(cols[7])),   # means (TODO width)
        max(9,  len(cols[8])),  # occupancy
    )

    # Initialize table printer
    tableprinter = Tableprinter(widths, separator=' | ')

    # Print the header line
    tableprinter.print_line(cols)
    tableprinter.print_separator()

    # Print data
    for i, row in enumerate(table, start=1):
        duration = row['arrival'] - row['departure']
        cols_from = (
            str(i),
            row['station_from'],
            row['platform_from'],
            row['departure'].strftime('%a, %d.%m.%y'),
            row['departure'].strftime('%H:%M'),
            ':'.join(six.text_type(duration).split(':')[:2]),
            row['change_count'],
            row['travelwith'],
            (lambda: u'1: %s' % row['occupancy1st'] if row['occupancy1st'] else u'-')(),
        )
        tableprinter.print_line(cols_from)

        cols_to = (
            '',
            row['station_to'],
            row['platform_to'],
            row['arrival'].strftime('%a, %d.%m.%y'),
            row['arrival'].strftime('%H:%M'),
            '',
            '',
            '',
            (lambda: u'2: %s' % row['occupancy2nd'] if row['occupancy2nd'] else u'-')(),
        )
        tableprinter.print_line(cols_to)

        tableprinter.print_separator()


def parse_connection(connection):
    """Process a connection object and return a dictionary with cleaned data."""

    data = {}
    con_from = connection['from']
    con_to = connection['to']

    data['station_from'] = con_from['station']['name']
    data['station_to'] = con_to['station']['name']
    data['departure'] = dateutil.parser.parse(con_from['departure'])
    data['arrival'] = dateutil.parser.parse(con_to['arrival'])
    data['platform_from'] = con_from['platform']
    data['platform_to'] = con_to['platform']
    data['change_count'] = six.text_type(connection['transfers'])
    data['travelwith'] = ', '.join(connection['products'])

    occupancies = {
        None: u'',
        -1: u'',
        0: u'Low',  # todo check
        1: u'Low',
        2: u'Medium',
        3: u'High',
    }

    data['occupancy1st'] = occupancies.get(connection['capacity1st'], u'')
    data['occupancy2nd'] = occupancies.get(connection['capacity2nd'], u'')

    return data


if __name__ == '__main__':
    main()
