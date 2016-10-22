# -*- coding: utf-8 -*-
import six
from .tableprinter import Tableprinter
# Output formats
class Formats(object):
    SIMPLE = 0
    FULL = 1

def displayConnections(connections, output_format):
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
