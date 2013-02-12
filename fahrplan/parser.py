# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime
import re
import logging

import six


def _process_tokens(tokens, sloppy_validation=False):
    """Parse input tokens.

    Take a list of tokens (usually ``sys.argv[1:]``) and parse the "human
    readable" input into a format suitable for machines.

    Args:
        tokens: List of tokens (usually ``sys.argv[1:]``.
        sloppy_validation: Set to True to enable less strict validation. Used
            mainly for testing, default False.

    Returns:
        A 2-tuple containing the unmapped data dictionary and the language
        string. For example:

        ({'to': 'bern', 'from': 'zürich', 'departure': '18:00'}, 'de')

    Raises:
        ValueError: If "from" or "to" arguments are missing or if both
            departure *and* arrival time are specified (as long as
            sloppy_validatoin is disabled).

    """
    if len(tokens) < 2:
        return {}, None

    keyword_dicts = {
        'en': {'from': 'from', 'to': 'to', 'via': 'via',
               'departure': 'departure', 'arrival': 'arrival'},
        'de': {'from': 'von', 'to': 'nach', 'via': 'via',
               'departure': 'ab', 'arrival': 'an'},
        'fr': {'from': 'de', 'to': 'à', 'via': 'via',
               'departure': 'départ', 'arrival': 'arrivée'},
    }

    # Detect language
    language = _detect_language(keyword_dicts, tokens)
    logging.info('Detected [%s] input' % language)

    # Keywords mapping
    keywords = dict((v, k) for k, v in six.iteritems(keyword_dicts[language]))
    logging.debug('Using keywords: ' + ', '.join(keywords.keys()))

    # Prepare variables
    data = {}
    stack = []

    def process_stack():
        """Process the stack. First item is the key, rest is value."""
        key = keywords.get(stack[0])
        value = ' '.join(stack[1:])
        data[key] = value
        stack[:] = []

    # Process tokens
    for token in tokens:
        if token in keywords.keys():
            if stack:
                process_stack()
        elif not stack:
            continue
        stack.append(token)
    process_stack()

    # Validate data
    if not sloppy_validation:
        if not ('from' in data and 'to' in data):
            raise ValueError('"from" and "to" arguments must be present!')
        if 'departure' in data and 'arrival' in data:
            raise ValueError('You can\'t specify both departure *and* arrival time.')

    return data, language


def _detect_language(keyword_dicts, tokens):
    """Detect the language of the tokens by finding the highest intersection
    with the keywords of a specific language."""
    intersection_count = lambda a, b: len(set(a).intersection(b))

    counts = []
    for lang, keywords in keyword_dicts.items():
        count = intersection_count(keywords.values(), tokens)
        counts.append((lang, count))

    language = max(counts, key=lambda x: x[1])[0]
    return language


def _parse_time(timestring, language):
    """Parse time tokens.

    Args:
        timestring: String containing a time specification.
        language: The language string (e.g. 'en' or 'de').

    Returns:
        Time string.

    Raises:
        ValueError: If time could not be parsed.

    """

    keywords = {
        'de': {
            'now': ['jetzt', 'sofort', 'nun'],
            'noon': ['mittag'],
            'midnight': ['mitternacht'],
            'at': ['um', 'am'],
        },
        'en': {
            'now': ['now', 'right now', 'immediately'],
            'noon': ['noon'],
            'midnight': ['midnight'],
            'at': ['at'],
        },
        'fr': {
            'now': ['maitenant'],
            'noon': ['midi'],
            'midnight': ['minuit'],
            'at': [],  # TODO: "à" clashes with top level keywords
        },
    }

    try:
        kws = keywords[language]
    except IndexError:
        raise ValueError('Invalid language: "%s"!' % language)

    # Ignore "at" keywords
    if timestring.split(' ', 1)[0] in kws['at']:
        timestring = timestring.split(' ', 1)[1]

    # Parse regular time strings
    regular_time_match = re.match(r'([0-2]?[0-9])[:\-\. ]([0-9]{2})', timestring)
    if regular_time_match:
        return ':'.join(regular_time_match.groups())

    if timestring.lower() in kws['now']:
        return datetime.now().strftime('%H:%M')
    if timestring.lower() in kws['noon']:
        return '12:00'
    if timestring.lower() in kws['midnight']:
        return '23:59'  # '00:00' would be the first minute of the day, not the last one.

    raise ValueError('Time string "%s" could not be parsed.' % timestring)


def parse_input(tokens):
    """Parse input tokens.

    Take a list of tokens (usually ``sys.argv[1:]``) and parse the "human
    readable" input into a format suitable for machines. The output format
    matches the format required by the Transport API.

    Args:
        tokens: List of tokens (usually ``sys.argv[1:]``.

    Returns:
        A 2-tuple containing the data dictionary and the language string. For
        example:

        ({'to': 'bern', 'from': 'zürich'}, 'de')

    Raises:
        ValueError: If "from" or "to" arguments are missing or if both
            departure *and* arrival time are specified.

    """
    # Process tokens, get data dict and language
    data, language = _process_tokens(tokens)

    # Map keys
    if 'departure' in data:
        data['time'] = _parse_time(data['departure'], language)
        del data['departure']
    if 'arrival' in data:
        data['time'] = _parse_time(data['arrival'], language)
        data['isArrivalTime'] = 1
        del data['arrival']

    logging.debug('Data: ' + repr(data))
    return data, language


    """
    transport.opendata.ch request params:
    x from
    x to
    x via
    - date
    x time
    x isArrivalTime
    - transportations
    - limit
    - page
    - direct
    - sleeper
    - couchette
    - bike
    """
