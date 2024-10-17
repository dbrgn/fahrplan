# -*- coding: utf-8 -*-
from rich.table import Table


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
    row = [str(i)]
    for p in [
            lambda x: [x['station_from'], x['station_to']],  # Station
            lambda x: [x.get('platform_from') or '-', x.get('platform_to') or '-'],  # Platform
            lambda x: [x[q].strftime('%d/%m/%y') for q in ['departure', 'arrival']],  # Date
            lambda x: [x[q].strftime('%H:%M') for q in ['departure', 'arrival']],  # Time
            lambda x: [str((x['arrival'] - x['departure'])).rsplit(':', 1)[0], ' '],  # Duration
            None,
            lambda x: [x['travelwith'], ' '],  # With
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
    table = Table(show_lines=True)
    # Alignments
    # Define columns
    table.add_column("#", justify="left", vertical="middle")
    table.add_column("Station", justify="left", vertical="top")
    table.add_column("Platform", justify="center", vertical="top")
    table.add_column("Date", justify="left", vertical="top")
    table.add_column("Time", justify="left", vertical="top")
    table.add_column("Duration", justify="center", vertical="top")
    table.add_column("Changes", justify="center", vertical="middle")
    table.add_column("With", justify="left", vertical="top")
    # Connection rows
    for i, connection in enumerate(connections):
        table.add_row(*_get_connection_row(i, connection))
    # Display
    return table
