# -*- coding: utf-8 -*-
import logging


def parse_input(tokens, sloppy_validation=False):
    """Take a list of tokens (usually ``sys.argv[1:]``) and parse the "human
    readable" input into a format suitable for machines.
   
    Keyword arguments:
     sloppy_validation -- Less strict validation, used mainly for testing (default False)

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
    intersection_count = lambda a, b: len(set(a).intersection(b))
    intersection_counts = [(lang, intersection_count(keywords.values(), tokens))
                           for lang, keywords in keyword_dicts.items()]
    language = max(intersection_counts, key=lambda x: x[1])[0]
    logging.info('Detected [%s] input' % language)

    # Prepare variables
    keywords = keyword_dicts[language]
    logging.debug('Using keywords: ' + ', '.join(keywords.values()))
    data = {}
    stack = []

    def process_stack():
        """Process the stack. First item is the key, rest is value."""
        key = stack[0]
        value = ' '.join(stack[1:])
        data[key] = value
        stack[:] = []

    # Process tokens
    for token in tokens:
        if token in keywords.values():
            if stack:
                process_stack()
        elif not stack:
            continue
        stack.append(token)
    process_stack()

    # Translate language
    # TODO this is sort of hackish... Could probably be done earlier.
    for neutral, translated in keywords.iteritems():
        if neutral != translated and translated in data:
            data[neutral] = data[translated]
            del data[translated]

    # Validate data
    if not sloppy_validation:
        if not ('from' in data and 'to' in data):
            raise ValueError('"from" and "to" arguments must be present!')
        if 'departure' in data and 'arrival' in data:
            raise ValueError('You can\'t specify both departure *and* arrival time.')

    logging.debug('Data: ' + repr(data))
    return data, language
