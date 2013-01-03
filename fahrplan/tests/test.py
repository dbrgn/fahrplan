# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import datetime

import six
import envoy
import gevent
from gevent import monkey
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    import unittest2 as unittest
else:
    import unittest

from .. import parser
from .. import meta

monkey.patch_socket()


BASE_COMMAND = 'python -m fahrplan.main'
ENCODING = sys.stdout.encoding or 'utf-8'


class TestBasicArgumentHandling(unittest.TestCase):

    def testTooFewArguments(self):
        args = ['', '-i', '-d']
        for arg in args:
            r = envoy.run(b'{0} {1}'.format(BASE_COMMAND, arg))
            self.assertEqual('Not enough arguments.\n', r.std_err)

    def testRequiredArgumentsMissing(self):
        r = envoy.run(b'{0} von bern'.format(BASE_COMMAND))
        self.assertEqual('Error: "from" and "to" arguments must be present!\n', r.std_err)

    def testVersionInfo(self):
        args = ['-v', '--version']
        for arg in args:
            r = envoy.run(b'{0} {1}'.format(BASE_COMMAND, arg))
            self.assertEqual('%s %s\n' % (meta.title, meta.version), r.std_out)

    def testHelp(self):
        args = ['-h', '--help']
        for arg in args:
            r = envoy.run(b'{0} {1}'.format(BASE_COMMAND, arg))
            title = '{meta.title}: {meta.description}'.format(meta=meta).encode(ENCODING)
            self.assertTrue(title in r.std_out)
            self.assertTrue(b'Usage:' in r.std_out)
            self.assertTrue(b'Options:' in r.std_out)
            self.assertTrue(b'Arguments:' in r.std_out)
            self.assertTrue(b'Examples:' in r.std_out)


class TestInputParsing(unittest.TestCase):

    valid_expected_result = {'arrival': '19:00', 'departure': '18:00', 'from': 'Zürich', 'to': 'Locarno', 'via': 'Genève'}

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
        tokens = 'from Zürich to Locarno via Genève departure 18:00 arrival 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('en', language)

    def testValidArgumentsDe(self):
        tokens = 'von Zürich nach Locarno via Genève ab 18:00 an 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('de', language)

    def testValidArgumentsFr(self):
        tokens = 'de Zürich à Locarno via Genève départ 18:00 arrivée 19:00'.split()
        data, language = parser._process_tokens(tokens, sloppy_validation=True)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('fr', language)

    def testNotEnoughArgument(self):
        tokens = 'from basel via bern'.split()
        self.assertRaises(ValueError, parser.parse_input, tokens)

    def testBasicDepartureTime(self):
        tokens = 'von basel nach bern ab 18:00'.split()
        expected = {'from': 'basel', 'time': '18:00', 'to': 'bern'}
        self.assertEqual(expected, parser.parse_input(tokens)[0])

    def testBasicArrivalTime(self):
        tokens = 'von basel nach bern an 18:00'.split()
        expected = {'from': 'basel', 'isArrivalTime': 1, 'time': '18:00', 'to': 'bern'}
        self.assertEqual(expected, parser.parse_input(tokens)[0])

    def testImmediateTimes(self):
        now = datetime.datetime.now().strftime('%H:%M')
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


class TestBasicQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup method that is only run once."""
        cmd = '{0} von basel nach zürich ab 14:00'.format(BASE_COMMAND)
        cls.r = envoy.run(cmd.encode(ENCODING))
        cls.rows = cls.r.std_out.split(b'\n')

    def returnStatus(self):
        """The command should return the status code 0."""
        self.assertEqual(0, self.r.status_code)

    def testRowCount(self):
        """A normal output table should have 14 rows."""
        self.assertEqual(15, len(self.rows))

    def testHeadline(self):
        """Test the headline items."""
        headline_items = ['Station', 'Platform', 'Date', 'Time', 'Duration', 'Chg.', 'Travel with', 'Occupancy']
        for item in headline_items:
            self.assertIn(item, self.rows[0])

    def testEnumeration(self):
        """Each row should be enumerated."""
        firstcol = [row[0] for row in self.rows[:-1]]
        self.assertEqual(list('#-1 -2 -3 -4 -'), firstcol)

    def testStationNames(self):
        """Station names should be "Basel SBB" and "Zürich HB"."""
        if six.PY3:  # quick and dirty
            self.assertTrue(self.rows[2].decode().startswith('1  | Basel SBB'))
            self.assertTrue(self.rows[3].decode().startswith('   | Zürich HB'))
        else:
            self.assertTrue(self.rows[2].startswith(b'1  | Basel SBB'))
            self.assertTrue(self.rows[3].startswith(b'   | Z\\xfcrich HB'))


class TestLanguages(unittest.TestCase):

    def testBasicQuery(self):
        """
        Test a query in three languages and assert that the output of all
        three queries is equal.

        The test is run using async gevent tasks, so that they run as close
        together as possible. (We don't want different output due to timing
        issues...)

        """
        args = ['von bern nach basel via zürich ab 15:00',
                'from bern to basel via zürich departure 15:00',
                'de bern à basel via zürich départ 15:00']
        jobs = [gevent.spawn(envoy.run, '{0} {1}'.format(BASE_COMMAND, arg).encode(ENCODING)) for arg in args]
        gevent.joinall(jobs, timeout=10)

        statuscodes = [job.value.status_code for job in jobs]
        self.assertEqual([0, 0, 0], statuscodes)

        stdout_values = [job.value.std_out for job in jobs]
        self.assertTrue(stdout_values[1:] == stdout_values[:-1])


class RegressionTests(unittest.TestCase):

    def testIss11(self):
        """Github issue #11:
        Don't allow both departure and arrival time."""
        args = 'von bern nach basel ab 15:00 an 16:00'
        query = envoy.run(b'{0} {1}'.format(BASE_COMMAND, args))
        self.assertEqual('Error: You can\'t specify both departure *and* arrival time.\n',
                query.std_err)

    def testIss13(self):
        """Github issue #13:
        Station not found: ValueError: max() arg is an empty sequence."""
        args = 'von zuerich manegg nach nach stadelhofen'
        query = envoy.run(b'{0} {1}'.format(BASE_COMMAND, args))
        self.assertEqual(0, query.status_code, 'Program terminated with statuscode != 0')


if __name__ == '__main__':
    unittest.main()
