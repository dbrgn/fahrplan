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

# Base configuration
API_URL = 'http://transport.opendata.ch/v1'
ENCODING = sys.stdout.encoding or 'utf-8'

# Output formats
class Formats(object):
    SIMPLE = 0
    FULL = 1
output_format = Formats.SIMPLE

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
    global output_format
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
                + ' -f, --full    Show full connection info, including changes\n'
                + ' -i, --info    Verbose output\n'
                + ' -d, --debug   Debug output\n'
                + ' -v, --version Show version number\n'
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
        if tokens[0] in ['-f', '--full']:
            output_format = Formats.FULL
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

    if not data['connections']:
        msg = 'No connections found from "%s" to "%s".' % \
              (data['from']['name'], data['to']['name'])
        print(msg.encode(ENCODING))
        sys.exit(0)


    """3. Process and output data."""

    include_sections = (output_format == Formats.FULL)
    connections = [parse_connection(c, include_sections) for c in data['connections']]

    # Define columns
    cols = (
        '#', 'Station', 'Platform', 'Date', 'Time',
        'Duration', 'Chg.', 'Travel with', 'Occupancy',
    )

    # Calculate and set column widths
    station_width = 0
    for connection in connections:
        for section in connection['sections']:
            maxlen = max([len(section['station_from']), len(section['station_to'])])
            if maxlen > station_width:
                station_width = maxlen
    travelwith_width = len(max([t['travelwith'] for t in connections], key=len))
    widths = (
        2,
        max(station_width, len(cols[1])),  # station
        max(4,  len(cols[2])),  # platform (TODO width)
        max(13, len(cols[3])),  # date
        max(5,  len(cols[4])),  # time
        max(5,  len(cols[5])),  # duration
        max(2,  len(cols[6])),  # changes
        max(travelwith_width, len(cols[7])),  # means (TODO width)
        max(9,  len(cols[8])),  # occupancy
    )

    # Initialize table printer
    tableprinter = Tableprinter(widths, separator=' | ')

    # Print the header line
    tableprinter.print_line(cols)
    tableprinter.print_separator()

    # Print data
    for i, conn in enumerate(connections, start=1):
        duration = conn['sections'][-1]['arrival'] - conn['sections'][0]['departure']
        for j, row in enumerate(conn['sections'], start=1):
            cols_from = (
                str(i) if j == 1 else '',
                row['station_from'],
                row['platform_from'],
                row['departure'].strftime('%a, %d.%m.%y'),
                row['departure'].strftime('%H:%M'),
                ':'.join(six.text_type(duration).split(':')[:2]) if j == 1 else '',
                conn['change_count'] if j == 1 else '',
                conn['travelwith'] if j == 1 else '',
                (lambda: '1: %s' % row['occupancy1st'] if row.get('occupancy1st') else '-')(),
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
                (lambda: '2: %s' % row['occupancy2nd'] if row.get('occupancy2nd') else '-')(),
            )
            tableprinter.print_line(cols_to)
            
            if j != len(conn['sections']):
                tableprinter.print_separator(cols=[1,2,3,4,8])
        tableprinter.print_separator()


def parse_connection(connection, include_sections=False):
    """Parse a connection.

    Process a connection object as returned from the API and return a
    dictionary with cleaned data.

    Args:
        connection: A connection dictionary as returned by the JSON API.
        include_sections: A boolean value determining whether to include the
            sections in the returned data set or not (default False).

    Returns:
        A dictionary containing cleaned data. If sections are enabled, they are
        contained in a list.

    """

    data = {}
    con_from = connection['from']
    con_to = connection['to']
    walk = False
    keyfunc = lambda s: s['departure']['departure']
    con_sections = sorted(connection['sections'], key=keyfunc)

    occupancies = {
        None: '',
        -1: '',
        0: 'Low',  # todo check
        1: 'Low',
        2: 'Medium',
        3: 'High',
    }

    def parse_section(con_section):
        departure = con_section['departure']
        arrival = con_section['arrival']
        journey = con_section.get('journey')
        walk = con_section.get('walk')
        section = {}
        section['station_from'] = departure['station']['name']
        section['station_to'] = arrival['station']['name']
        section['departure'] = dateutil.parser.parse(departure['departure'])
        section['arrival'] = dateutil.parser.parse(arrival['arrival'])
        section['platform_from'] = 'Walk' if walk else departure['platform']
        section['platform_to'] = arrival['platform']
        if walk:
            section['occupancy1st'] = ''
            section['occupancy2nd'] = ''
        elif journey:
            section['occupancy1st'] = occupancies.get(con_section['journey']['capacity1st'], '')
            section['occupancy2nd'] = occupancies.get(con_section['journey']['capacity2nd'], '')
        else:
            section['occupancy1st'] = occupancies.get(connection['capacity1st'], '')
            section['occupancy2nd'] = occupancies.get(connection['capacity2nd'], '')
        return section

    data['sections'] = []
    if include_sections:
        for con_section in con_sections:
            section = parse_section(con_section)
            if con_section.get('walk'):
                walk = True
            data['sections'].append(section)
    else:
        con_section = {'departure': connection['from'], 'arrival': connection['to']}
        data['sections'].append(parse_section(con_section))

    data['change_count'] = six.text_type(connection['transfers'])
    data['travelwith'] = ', '.join(connection['products'])
    if walk:
        data['travelwith'] += ', Walk'
    data['occupancy1st'] = occupancies.get(connection['capacity1st'], '')
    data['occupancy2nd'] = occupancies.get(connection['capacity2nd'], '')

    return data


if __name__ == '__main__':
    main()
