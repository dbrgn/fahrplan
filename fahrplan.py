#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from datetime import date, time, datetime
import json
import requests
from clint.textui import puts, colored
from clint.textui import columns

API_URL = 'http://transport.opendata.ch/v1'


def main():
    parser = argparse.ArgumentParser(
        description='Query the SBB timetables.',
        epilog='Disclaimer: This is not an official SBB app. The correctness \
                of the data is not guaranteed.')
    parser.add_argument('start')
    parser.add_argument('destination')
    parser.add_argument('-v', '--via', help='set a via')
    parser.add_argument('-d', '--date', type=date, default=date.today(), help='departure or arrival date')
    parser.add_argument('-t', '--time', type=time, default=datetime.time(datetime.today()), help='departure or arrival time')
    parser.add_argument('-m', '--mode', choices=['dep', 'arr'], default='dep', help='time mode (date/time are departure or arrival)')
    parser.add_argument('--verbosity', type=int, choices=range(1, 4), default=2)
    parser.add_argument('--version', action='version', version='%(prog)s v0.1')
    args = parser.parse_args()
    args.mode = 1 if args.mode == 'arr' else 0

    url, params = build_request(args)
    response = requests.get(url, params=params)
    data = json.loads(response.content)
    connections = data['connections']


    """Table width:

    max(len(station)) + 12 + 8 + 5 + 2 + max(len(means)) + 7

    """

    table = [parse_connection(c) for c in connections]

    # Get column widths
    station_width = len(max([t['station_from'] for t in table] + \
                            [t['station_to'] for t in table]))
    cols = (
        u'Station',
        u'Date',
        u'Time',
        u'Duration',
        u'Changes',
        u'Means',
        u'Capacity'
    )
    widths = (
        max(station_width, len(cols[0])),
        max(12, len(cols[1])),
        max(8,  len(cols[2])),
        max(5,  len(cols[3])),
        max(2,  len(cols[4])),
        max(4,  len(cols[5])), # todo
        max(7,  len(cols[6])),
    )
    pairs = map(list, zip(cols, [w + 1 for w in widths]))
    puts(columns(*pairs))

    separator = u''.join('-' * (w + 1) + '|' for w in widths)
    print separator

    for row in table:
        cols = [
            row['station_from'].encode('latin1', errors='replace'),
            u'Fr, 12.34.56',
            row['departure'],
            u'??:??',
            u'?',
            u'todo',
            row['capacity2nd'].encode('latin1', errors='replace'),
        ]
        pairs = map(list, zip(cols, [w + 1 for w in widths]))
        puts(columns(*pairs))
        print separator


def build_request(args):
    url = '%s/connections' % API_URL
    params = {
        'from': args.start,
        'to': args.destination,
    }
    return url, params


def parse_connection(connection):
    con_from = connection['from']
    con_to = connection['to']
    data = {}

    data['station_from'] = con_from['station']['name']
    data['station_to'] = con_to['station']['name']
    data['departure'] = con_from['departure'][:5]
    data['platform'] = con_from['platform']

    try:
        capacity1st = int(con_from['prognosis']['capacity1st'])
    except TypeError:
        data['capacity1st'] = u'?'
    else:
        cap_string = u'*' * capacity1st + u'.' * (3 - capacity1st)
        data['capacity1st'] = cap_string

    try:
        capacity2nd = int(con_from['prognosis']['capacity2nd'])
    except TypeError:
        data['capacity2nd'] = u'?'
    else:
        cap_string = u'*' * capacity2nd + u'.' * (3 - capacity2nd)
        data['capacity2nd'] = cap_string
    
    return data


if __name__ == '__main__':
    main()
