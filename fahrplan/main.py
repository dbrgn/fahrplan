#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A SBB/CFF/FFS commandline based timetable client.
# Copyright (C) 2012-2014 Danilo Bargen
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
import logging
import argparse
import six

from . import meta
from .parser import parse_input
from .api import get_connections
from .display import Formats, connectionsTable
from .helpers import perror

# Base configuration
ENCODING = sys.stdout.encoding or 'utf-8'


def main():
    output_format = Formats.SIMPLE
    proxy_host = None

    # 1. Parse command line arguments
    parser = argparse.ArgumentParser(epilog='Arguments:\n'
                + u' You can use natural language arguments using the following\n'
                + u' keywords in your desired language:\n'
                + u' en -- from, to, via, departure, arrival\n'
                + u' de -- von, nach, via, ab, an\n'
                + u' fr -- de, à, via, départ, arrivée\n'
                + u'\n'
                + u' You can also use natural time and date specifications in your language, like:\n'
                + u' - "now", "immediately", "at noon", "at midnight",\n'
                + u' - "tomorrow", "monday", "in 2 days", "22/11".\n'
                + u'\n'
                + u'Examples:\n'
                + u' fahrplan from thun to burgdorf\n'
                + u' fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35\n'
                + u' fahrplan de lausanne à vevey arrivée minuit\n'
                + u' fahrplan from Bern to Zurich departure 13:00 monday\n'
                + u' fahrplan -p proxy.mydomain.ch:8080 de lausanne à vevey arrivée minuit\n'
                + u'\n', formatter_class=argparse.RawDescriptionHelpFormatter, prog=meta.title, description=meta.description, add_help=False)
    parser.add_argument("--full", "-f", action="store_true", help="Show full connection info, including changes")
    parser.add_argument("--info", "-i", action="store_true", help="Verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug output")
    parser.add_argument("--help", "-h", action="store_true", help="Show this help")
    parser.add_argument("--version", "-v", action="store_true", help="Show version number")
    parser.add_argument("--proxy", "-p", help="Use proxy for network connections (host:port)")
    parser.add_argument("request", nargs=argparse.REMAINDER)
    options = parser.parse_args()

    # Version
    if options.version:
        print('{meta.title} {meta.version}'.format(meta=meta))
        sys.exit(0)

    # No request or help
    if len(options.request) == 0 or options.help:
        if six.PY2:
            print(parser.format_help().encode(ENCODING))
        else:
            parser.print_help()
        sys.exit(0)

    # Options
    if options.full:
        output_format = Formats.FULL
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    if options.proxy is not None:
        proxy_host = options.proxy

    # Parse user request
    if six.PY2:
        options.request = [o.decode(ENCODING) for o in options.request]
    try:
        args, language = parse_input(options.request)
    except ValueError as e:
        perror('Error:', e)
        sys.exit(1)

    # 2. API request
    data = get_connections(args, (output_format == Formats.FULL), proxy_host)
    connections = data["connections"]

    if not connections:
        print("No connections found")
        sys.exit(0)

    # 3. Output data
    table = connectionsTable(connections, output_format)
    if six.PY2:
        table = table.encode(ENCODING)
    print(table)

if __name__ == '__main__':
    main()
