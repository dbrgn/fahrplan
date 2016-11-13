# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime, timedelta
import re
import logging

import six

keywords = {
    'de': {
        'now': ['jetzt', 'sofort', 'nun'],
        'noon': ['mittag'],
        'midnight': ['mitternacht'],
        'today': ["heute"],
        'tomorrow': ["morgen"],
        'at': ['um', 'am'],
        'days': [r'in (\d+) tagen'],
        'weekdays': ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"],
    },
    'en': {
        'now': ['now', 'right now', 'immediately'],
        'noon': ['noon'],
        'midnight': ['midnight'],
        'today': ["today"],
        'tomorrow': ["tomorrow"],
        'at': ['at'],
        'days': [r'in (\d+) days'],
        'weekdays': ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    },
    'fr': {
        'now': ['maitenant'],
        'noon': ['midi'],
        'midnight': ['minuit'],
        'today': ["aujourd'hui"],
        'tomorrow': ["demain"],
        'days': [r"dans (\d+) jours"],
        'at': [],  # TODO: "à" clashes with top level keywords
        'weekdays': ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
    },
}


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

    def intersection_count(a, b):
        return len(set(a).intersection(b))

    counts = []
    for lang, keywords in keyword_dicts.items():
        count = intersection_count(keywords.values(), tokens)
        counts.append((lang, count))

    language = max(counts, key=lambda x: x[1])[0]
    return language


def _parse_date(datestring, keywords):
    """Parse date tokens.

    Args:
        datestring: String containing a date specification.
        keywords: Language keywords

    Returns:
        date string.

    Raises:
        ValueError: If time could not be parsed.

    """
    date = None
    days_shift = None
    # Keywords
    for i, d in enumerate(["today", "tomorrow"]):
        if any([t in datestring for t in keywords[d]]):
            days_shift = i
    # Weekdays
    for i, d in enumerate(keywords["weekdays"]):
        if d in datestring:
            days_shift = i - datetime.now().weekday()
            if days_shift <= 0:
                days_shift += 7
    # Shifts
    if days_shift is None:
        for pattern in keywords["days"]:
            days_re = re.search(pattern, datestring)
            if days_re:
                try:
                    days_shift = int(days_re.group(1))
                except:
                    pass

    if days_shift is not None:
        return datetime.now() + timedelta(days=days_shift)

    # Regular date strings
    for dateformat in [[r"(\d{2}/\d{2}/\d{4})", "%d/%m/%Y"], [r"(\d{2}/\d{2})", "%d/%m"]]:
        days_re = re.search(dateformat[0], datestring)
        if days_re:
            try:
                date = datetime.strptime(days_re.group(1), dateformat[1])
            except:
                continue
            if date.year == 1900:
                date = date.replace(year=datetime.now().year)
            break

    if date is not None:
        return date.strftime("%Y/%m/%d")

    return None


def _parse_time(timestring, keywords):
    """Parse time tokens.

    Args:
        timestring: String containing a time specification.
        keywords: Language keywords

    Returns:
        Time string.

    Raises:
        ValueError: If time could not be parsed.

    """

    # Ignore "at" keywords
    if timestring.split(' ', 1)[0] in keywords['at']:
        timestring = timestring.split(' ', 1)[1]

    # Parse regular time strings
    # regular_time_match = re.search(r'([0-2]?[0-9])[:\-\. ]([0-9]{2})', timestring)
    regular_time_match = re.search(r'(?<!/)(\d{2})(?::*)(\d{2})', timestring)
    if regular_time_match:
        return ':'.join(regular_time_match.groups())
    timestring = timestring.lower()
    if timestring in keywords['now']:
        return datetime.now().strftime('%H:%M')
    if timestring in keywords['noon']:
        return '12:00'
    if timestring in keywords['midnight']:
        return '23:59'  # '00:00' would be the first minute of the day, not the last one.
    raise ValueError('Time is missing or could not be parsed')


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
    if data == {}:
        return data, language
    try:
        kws = keywords[language]
    except IndexError:
        raise ValueError('Invalid language: "%s"!' % language)
    # Map keys
    for t in ["departure", "arrival"]:
        if t in data:
            data["time"] = _parse_time(data[t], kws)
            date = _parse_date(data[t], kws)
            if date is not None:
                data["date"] = date
            if t == "arrival":
                data['isArrivalTime'] = 1
            del data[t]

    logging.debug('Data: ' + repr(data))
    return data, language
