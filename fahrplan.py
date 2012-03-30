#!/usr/bin/env python
# coding=utf-8

import argparse
from datetime import date, time, datetime
import json
import requests
import clint

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

    url, params = buildRequest(args)
    response = requests.get(url, params=params)
    data = json.loads(response.content)
    connections = data['connections']

    for connection in connections:
        print 'Departure: %s Platform %s' % \
            (connection['from']['departure'], connection['from']['platform'])


def buildRequest(args):
    url = '%s/connections' % API_URL
    params = {
        'from': args.start,
        'to': args.destination,
    }
    return url, params


if __name__ == '__main__':
    main()
