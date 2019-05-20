#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A SBB/CFF/FFS commandline based timetable client.
# Copyright (C) 2012-2019 Danilo Bargen
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
import logging
import argparse

from . import meta
from .parser import parse_input
from .api import get_connections
from .display import Formats, connectionsTable
from .helpers import perror


def main():
    output_format = Formats.SIMPLE
    proxy_host = None

    # 1. Parse command line arguments
    parser = argparse.ArgumentParser(epilog='Arguments:\n'
                + ' You can use natural language arguments using the following\n'
                + ' keywords in your desired language:\n'
                + ' en -- from, to, via, departure, arrival\n'
                + ' de -- von, nach, via, ab, an\n'
                + ' fr -- de, à, via, départ, arrivée\n'
                + '\n'
                + ' You can also use natural time and date specifications in your language, like:\n'
                + ' - "now", "immediately", "at noon", "at midnight",\n'
                + ' - "tomorrow", "monday", "in 2 days", "22/11".\n'
                + '\n'
                + 'Examples:\n'
                + ' fahrplan from thun to burgdorf\n'
                + ' fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35\n'
                + ' fahrplan de lausanne à vevey arrivée minuit\n'
                + ' fahrplan from Bern to Zurich departure 13:00 monday\n'
                + ' fahrplan -p proxy.mydomain.ch:8080 de lausanne à vevey arrivée minuit\n'
                + '\n', formatter_class=argparse.RawDescriptionHelpFormatter, prog=meta.title, description=meta.description, add_help=False)
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
    print(table)

if __name__ == '__main__':
    main()
