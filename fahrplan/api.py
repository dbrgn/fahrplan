# -*- coding: utf-8 -*-
import requests
import logging
import json
import dateutil.parser
import sys
from .helpers import perror

API_URL = 'http://transport.opendata.ch/v1'


def _api_request(action, params, proxy=None):
    """
    Perform an API request on transport.opendata.ch
    """
    # Send request
    url = "{}/{}".format(API_URL, action)
    kwargs = {'params': params}
    if proxy is not None:
        kwargs['proxies'] = {'http': proxy}
    try:
        response = requests.get(url, **kwargs)
    except requests.exceptions.ConnectionError:
        perror('Error: Could not reach network.')
        sys.exit(1)

    # Check response status
    logging.debug('Response status: {0!r}'.format(response.status_code))
    if not response.ok:
        verbose_status = requests.status_codes._codes[response.status_code][0]
        perror('Server Error: HTTP {} ({})'.format(response.status_code, verbose_status))
        sys.exit(1)

    # Convert response to json
    try:
        return json.loads(response.text)
    except ValueError:
        logging.debug('Response status code: {0}'.format(response.status_code))
        logging.debug('Response content: {0!r}'.format(response.content))
        perror('Error: Invalid API response (invalid JSON)')
        sys.exit(1)


def _parse_section(con_section, connection):
    """
    Parse the section of a connection
    """
    departure = con_section['departure']
    arrival = con_section['arrival']
    journey = con_section.get('journey')
    walk = con_section.get('walk')
    section = {}
    section['station_from'] = departure['station']['name']
    section['station_to'] = arrival['station']['name']
    if journey is not None:
        section['travelwith'] = '{} {}'.format(journey['category'], journey['number'])
    else:
        section['travelwith'] = ''
    section['departure'] = dateutil.parser.parse(departure['departure'])
    section['arrival'] = dateutil.parser.parse(arrival['arrival'])
    section['platform_from'] = "" if walk else departure['platform']
    section['platform_to'] = arrival['platform']
    return section


def _parse_connection(connection, include_sections=False):
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
    walk = False

    def keyfunc(s):
        return s['departure']['departure']
    data['change_count'] = str(connection['transfers'])
    data['travelwith'] = ', '.join(
        '{} {}'.format(section['journey']['category'], section['journey']['number'])
        for section
        in connection['sections']
        if section['journey'] is not None
    )

    # Sections
    con_sections = sorted(connection['sections'], key=keyfunc)
    data['sections'] = []
    if include_sections:
        # Full display
        for con_section in con_sections:
            section = _parse_section(con_section, connection)
            if con_section.get('walk'):
                walk = True
            data["sections"].append(section)
    else:
        # Shortened display, parse only departure and arrivals sections
        section = _parse_section(con_sections[0], connection)
        to = _parse_section(con_sections[-1], connection)
        for p in ["station_to", "arrival"]:
            section[p] = to[p]
        # Get information from connection
        for p in ["travelwith", "change_count"]:
            section[p] = data[p]
        data['sections'] = [section]

    # Walk
    if walk:
        data['travelwith'] += ', Walk'

    return data


def get_connections(request, include_sections=False, proxy=None):
    """
    Get the connections of a request
    """
    data = _api_request("connections", request, proxy)
    data["connections"] = [_parse_connection(c, include_sections) for c in data["connections"]]
    return data
