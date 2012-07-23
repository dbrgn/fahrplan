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

import sys
import json
import logging

import requests
import dateutil.parser

import meta
from tableprinter import Tableprinter

API_URL = 'http://transport.opendata.ch/v1'
ENCODING = sys.stdout.encoding or 'utf-8'
__version__ = meta.version


def main():

    """1. Parse arguments."""

    def assert_enough_arguments(args):
        if len(args) <= 1:
            print >> sys.stderr, 'Not enough arguments.'
            sys.exit(1)

    assert_enough_arguments(sys.argv)

    tokens = sys.argv[1:]
    while tokens and tokens[0].startswith('-'):
        if tokens[0] in ['-h', '--help']:
            print '%s: %s' % (meta.title, meta.description)
            print
            print 'Usage:'
            print ' %s [options] arguments' % meta.title
            print
            print 'Options:'
            print ' -v, --version Show version number'
            print ' -i, --info    Verbose output'
            print ' -d, --debug   Debug output'
            print ' -h, --help    Show this help'
            print
            print 'Arguments:'
            print ' You can use natural language arguments using the following'
            print ' keywords in your desired language:'
            print ' en -- from, to, via, departure, arrival'
            print ' de -- von, nach, via, ab, an'
            print ' fr -- de, à, via, départ, arrivée'
            print
            print 'Examples:'
            print ' fahrplan from thun to burgdorf'
            print ' fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35'
            print
            sys.exit(0)
        if tokens[0] in ['-v', '--version']:
            print '%s %s' % (meta.title, meta.version)
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
        print >> sys.stderr, 'Error: %s' % e
        sys.exit(1)


    """2. Do API request."""

    url, params = build_request(args)
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.ConnectionError:
        print >> sys.stderr, 'Error: Could not reach network.'
        sys.exit(1)

    logging.debug('Response status: %s' % repr(response.status_code))

    if not response.ok:
        verbose_status = requests.status_codes._codes[response.status_code][0]
        print >> sys.stderr, 'Server Error: HTTP %s (%s)' % \
                (response.status_code, verbose_status)
        sys.exit(1)

    try:
        data = json.loads(response.text)
    except ValueError:
        logging.debug('Response status code: %s' % response.status_code)
        logging.debug('Response content: %s' % repr(response.content))
        print >> sys.stderr, 'Error: Invalid API response (invalid JSON)'
        sys.exit(1)

    connections = data['connections']

    if not connections:
        msg = 'No connections found from "%s" to "%s".' % \
                (data['from']['name'], data['to']['name'])
        print msg.encode(ENCODING)
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
            ':'.join(unicode(duration).split(':')[:2]),
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


def parse_input(tokens, sloppy_validation=False):
    """Parse the human-like input (usually `sys.argv[1:]`).

    Keyword arguments:
     sloppy_validation -- Less strict validation, used mainly for testing (default False)

    """

    if len(tokens) < 2:
        return {}, None

    keyword_dicts = {
        'en': {'from': 'from', 'to': 'to', 'via': 'via', 'departure': 'departure', 'arrival': 'arrival'},
        'de': {'from': 'von', 'to': 'nach', 'via': 'via', 'departure': 'ab', 'arrival': 'an'},
        'fr': {'from': 'de', 'to': 'à', 'via': 'via', 'departure': 'départ', 'arrival': 'arrivée'},
    }

    # Detect language
    intersection_count = lambda a, b: len(set(a).intersection(b))
    intersection_counts = [(lang, intersection_count(keywords.values(), tokens))
            for lang, keywords in keyword_dicts.items()]
    language = max(intersection_counts, key=lambda x: x[1])[0]
    logging.info('Detected [%s] input' % language)

    # Prepare variables
    keywords = keyword_dicts[language]
    logging.debug('Using keywords: ' + ', '.join(keywords.values()))
    data = {}
    stack = []

    def process_stack():
        """Process the stack. First item is the key, rest is value."""
        key = stack[0]
        value = ' '.join(stack[1:])
        data[key] = value
        stack[:] = []

    # Process tokens
    for token in tokens:
        if token in keywords.values():
            if stack:
                process_stack()
        elif not stack:
            continue
        stack.append(token)
    process_stack()

    # Translate language
    # TODO this is sort of hackish... Could probably be done earlier.
    for neutral, translated in keywords.iteritems():
        if neutral != translated and translated in data:
            data[neutral] = data[translated]
            del data[translated]

    # Validate data
    if not sloppy_validation:
        if not ('from' in data and 'to' in data):
            raise ValueError('"from" and "to" arguments must be present!')
        if 'departure' in data and 'arrival' in data:
            raise ValueError('You can\'t specify both departure *and* arrival time.')

    logging.debug('Data: ' + repr(data))
    return data, language


def build_request(args):
    """Get the argument dictionary and return a url and the url params."""

    url = '%s/connections' % API_URL
    params = {
        'from': args['from'],
        'to': args['to'],
    }
    if 'via' in args:
        params['via'] = args.get('via')
    if 'departure' in args:
        params['time'] = args.get('departure')
    if 'arrival' in args:
        params['time'] = args.get('arrival')
        params['isArrivalTime'] = 1
    return url, params


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
    data['change_count'] = unicode(connection['transfers'])
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
