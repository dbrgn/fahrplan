# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import sys
from datetime import datetime

from subprocess import Popen, PIPE
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    import unittest2 as unittest
else:
    import unittest

from .. import meta
from .. import parser


BASE_COMMAND = 'python -m fahrplan.main'
try:
    ENCODING = sys.stdout.encoding or 'utf-8'
except AttributeError:
    ENCODING = 'utf-8'


# Run command
class CommandOutput(object):
    def __init__(self, stdout, stderr, code):
        self.std_err = stderr
        self.std_out = stdout
        self.status_code = code


def run_command(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return CommandOutput(stdout.decode(ENCODING), stderr.decode(ENCODING), p.returncode)


class TestBasicArgumentHandling(unittest.TestCase):

    def testRequiredArgumentsMissing(self):
        r = run_command('{0} von bern'.format(BASE_COMMAND))
        self.assertEqual('Error: "from" and "to" arguments must be present!\n', r.std_err)

    def testVersionInfo(self):
        args = ['-v', '--version', '-d -i -v']
        for arg in args:
            r = run_command('{0} {1}'.format(BASE_COMMAND, arg))
            self.assertEqual('%s %s\n' % (meta.title, meta.version), r.std_out)

    def testHelp(self):
        args = ['-h', '--help', '-d -i --help']
        for arg in args:
            r = run_command('{0} {1}'.format(BASE_COMMAND, arg))
            self.assertTrue(meta.description in r.std_out)
            self.assertTrue('usage:' in r.std_out)
            self.assertTrue('optional arguments:' in r.std_out)
            self.assertTrue('positional arguments:' in r.std_out)
            self.assertTrue('Examples:' in r.std_out)


class TestInputParsing(unittest.TestCase):

    valid_expected_result = {
        'arrival': '19:00',
        'departure': '18:30',
        'from': 'Zürich',
        'to': 'Locarno',
        'via': 'Genève',
    }

    def testEmptyArguments(self):
        tokens = []
        data, language = parser.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneValidArgument(self):
        tokens = 'from'.split()
        data, language = parser.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneInvalidArgument(self):
        tokens = 'foobar'.split()
        data, language = parser.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testValidArgumentsEn(self):
        tokens = 'from Zürich to Locarno via Genève departure 18:30 arrival 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('en', language)

    def testValidArgumentsDe(self):
        tokens = 'von Zürich nach Locarno via Genève ab 18:30 an 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('de', language)

    def testValidArgumentsFr(self):
        tokens = 'de Zürich à Locarno via Genève départ 18:30 arrivée 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('fr', language)

    def testNotEnoughArgument(self):
        tokens = 'from basel via bern'.split()
        self.assertRaises(ValueError, parser.parse_input, tokens)

    def testBasicDepartureTime(self):
        tokens = 'von basel nach bern ab 1945'.split()
        expected = {'from': 'basel', 'time': '19:45', 'to': 'bern'}
        self.assertEqual(expected, parser.parse_input(tokens)[0])

    def testBasicArrivalTime(self):
        tokens = 'von basel nach bern an 18:00'.split()
        expected = {'from': 'basel', 'isArrivalTime': 1, 'time': '18:00', 'to': 'bern'}
        self.assertEqual(expected, parser.parse_input(tokens)[0])

    def testImmediateTimes(self):
        now = datetime.now().strftime('%H:%M')
        queries = [
            'von basel nach bern ab jetzt'.split(),
            'von basel nach bern ab sofort'.split(),
            'from basel to bern departure now'.split(),
            'from basel to bern departure right now'.split(),
            'from basel to bern departure immediately'.split(),
            'de basel à bern départ maitenant'.split(),
        ]
        for tokens in queries:
            data, _ = parser.parse_input(tokens)
            self.assertEqual(now, data['time'])

    def testNoonTimes(self):
        queries = [
            'von basel nach bern ab mittag'.split(),
            'from basel to bern departure noon'.split(),
            'de basel à bern départ midi'.split(),
        ]
        for tokens in queries:
            data, _ = parser.parse_input(tokens)
            self.assertEqual('12:00', data['time'])

    def testMidnightTimes(self):
        queries = [
            'von basel nach bern ab mitternacht'.split(),
            'from basel to bern departure midnight'.split(),
            'de basel à bern départ minuit'.split(),
        ]
        for tokens in queries:
            data, _ = parser.parse_input(tokens)
            self.assertEqual('23:59', data['time'])

    def testAtTimes(self):
        queries = [
            'von basel nach bern ab am mittag'.split(),
            'von basel nach bern ab um 12:00'.split(),
            'from basel to bern departure at noon'.split(),
            'from basel to bern departure at 12:00'.split(),
        ]
        for tokens in queries:
            data, _ = parser.parse_input(tokens)
            self.assertEqual('12:00', data['time'])

    def testDates(self):
        year = datetime.now().year
        queries = [
            'von basel nach bern ab 22/10/2016 13:00'.split(),
            'von basel nach bern ab um 22/10 13:00'.split(),
            'from basel to bern departure 22/10 13:00'.split(),
            'from basel to bern departure 22/10 13:00'.split(),
        ]
        for tokens in queries:
            data, _ = parser.parse_input(tokens)
            self.assertEqual('13:00', data['time'])
            self.assertEqual('{}/10/22'.format(year), data['date'])


class TestBasicQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup method that is only run once."""
        cmd = '{0} von basel nach zürich ab 07:00'.format(BASE_COMMAND)
        cls.r = run_command(cmd)
        cls.rows = cls.r.std_out.split('\n')

    def returnStatus(self):
        """The command should return the status code 0."""
        self.assertEqual(0, self.r.status_code)

    def testRowCount(self):
        """A normal output table should have 16 rows."""
        self.assertEqual(16, len(self.rows))

    def testHeadline(self):
        """Test the headline items."""
        headline_items = ['Station', 'Platform', 'Date', 'Time',
                          'Duration', 'Chg.', 'With', 'Occupancy']
        for item in headline_items:
            self.assertIn(item, self.rows[1])

    def testStationNames(self):
        """Station names should be "Basel SBB" and "Zürich HB"."""
        self.assertTrue("Basel SBB" in self.rows[3])
        self.assertTrue("Zürich HB" in self.rows[4])


class TestLanguages(unittest.TestCase):

    def testBasicQuery(self):
        """
        Test a query in three languages and assert that the output of all
        three queries is equal.

        """
        args = ['von bern nach basel via zürich ab 15:00',
                'from bern to basel via zürich departure 15:00',
                'de bern à basel via zürich départ 15:00']
        jobs = [run_command('{0} {1}'.format(BASE_COMMAND, arg)) for arg in args]

        statuscodes = [job.status_code for job in jobs]
        self.assertEqual([0, 0, 0], statuscodes)

        stdout_values = [job.std_out for job in jobs]
        self.assertTrue(stdout_values[1:] == stdout_values[:-1])


class RegressionTests(unittest.TestCase):

    def testIss11(self):
        """
        Github issue #11:
        Don't allow both departure and arrival time.
        """
        args = 'von bern nach basel ab 15:00 an 16:00'
        query = run_command('{0} {1}'.format(BASE_COMMAND, args))
        self.assertEqual('Error: You can\'t specify both departure *and* arrival time.\n',
                query.std_err)

    def testIss13(self):
        """
        Github issue #13:
        Station not found: ValueError: max() arg is an empty sequence.
        """
        args = 'von zuerich manegg nach nach stadelhofen'
        query = run_command('{0} {1}'.format(BASE_COMMAND, args))
        self.assertEqual(0, query.status_code, 'Program terminated with statuscode != 0')


if __name__ == '__main__':
    unittest.main()
