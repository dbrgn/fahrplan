# -*- coding: utf-8 -*-
from texttable import Texttable


# Output formats
class Formats(object):
    SIMPLE = 0
    FULL = 1


def _get_connection_row(i, connection):
    """
    Get table row for connection.
    """
    sections = connection['sections']
    # Create row
    row = [i]
    for p in [
            lambda x: [x['station_from'], x['station_to']],  # Station
            lambda x: [x.get('platform_from') or '-', x.get('platform_to') or '-'],  # Platform
            lambda x: [x[q].strftime('%d/%m/%y') for q in ['departure', 'arrival']],  # Date
            lambda x: [x[q].strftime('%H:%M') for q in ['departure', 'arrival']],  # Time
            lambda x: [str((x['arrival'] - x['departure'])).rsplit(':', 1)[0], ' '],  # Duration
            None,
            lambda x: [x['travelwith'], ' '],  # With
            lambda x: ['1: ' + x['occupancy1st'], '2: ' + x['occupancy2nd']]  # Occupancy
    ]:
        if p is None:
            row.append(connection['change_count'])
        else:
            inner = ['\n'.join(p(s)) for s in sections]
            row.append('\n \n'.join(inner))
    return row


def connectionsTable(connections, output_format):
    """
    Get connections in the given output format.
    """
    table = Texttable(max_width=0)
    # Alignments
    table.set_cols_valign(['m', 't', 't', 't', 't', 't', 'm', 't', 't'])
    table.set_cols_align(['l', 'l', 'c', 'l', 'l', 'c', 'c', 'l', 'l'])
    # Header
    table.add_row(['#', 'Station', 'Platform', 'Date', 'Time', 'Duration', 'Chg.', 'With', 'Occupancy'])
    # Connection rows
    for i, connection in enumerate(connections):
        table.add_row(_get_connection_row(i, connection))
    # Display
    return table.draw()
