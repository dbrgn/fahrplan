import unittest2 as unittest
import envoy
import gevent
import main
import meta


from gevent import monkey
monkey.patch_socket()


BASE_COMMAND = 'python main.py'


class TestBasicArgumentHandling(unittest.TestCase):

    def testTooFewArguments(self):
        args = ['', '-i', '-d']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertEqual('Not enough arguments.\n', r.std_err)

    def testRequiredArgumentsMissing(self):
        r = envoy.run('%s von bern' % BASE_COMMAND)
        self.assertEqual('Error: "from" and "to" arguments must be present!\n', r.std_err)

    def testVersionInfo(self):
        args = ['-v', '--version']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertEqual('%s %s\n' % (meta.title, meta.version), r.std_out)

    def testHelp(self):
        args = ['-h', '--help']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertTrue('%s: %s' % (meta.title, meta.description) in r.std_out)
            self.assertTrue('Usage:' in r.std_out)
            self.assertTrue('Options:' in r.std_out)
            self.assertTrue('Arguments:' in r.std_out)
            self.assertTrue('Examples:' in r.std_out)


class TestInputParsing(unittest.TestCase):

    valid_expected_result = {'arrival': '19:00', 'departure': '18:00', 'from': 'Zürich', 'to': 'Locarno', 'via': 'Genève'}

    def testEmptyArguments(self):
        tokens = []
        data, language = main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneValidArgument(self):
        tokens = ['from']
        data, language = main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneInvalidArgument(self):
        tokens = ['foobar']
        data, language = main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testValidArgumentsEn(self):
        tokens = ['from', 'Zürich', 'to', 'Locarno', 'via', 'Genève', 'departure', '18:00', 'arrival', '19:00']
        data, language = main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('en', language)

    def testValidArgumentsDe(self):
        tokens = ['von', 'Zürich', 'nach', 'Locarno', 'via', 'Genève', 'ab', '18:00', 'an', '19:00']
        data, language = main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('de', language)

    def testValidArgumentsFr(self):
        tokens = ['de', 'Zürich', 'à', 'Locarno', 'via', 'Genève', 'départ', '18:00', 'arrivée', '19:00']
        data, language = main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('fr', language)

    def testNotEnoughArgument(self):
        tokens = ['from', 'basel', 'via', 'bern']
        self.assertRaises(ValueError, main.parse_input, tokens)


class TestBasicQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup method that is only run once."""
        cls.r = envoy.run('%s von basel nach zürich ab 14:00' % BASE_COMMAND)
        cls.rows = cls.r.std_out.split('\n')

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
        self.assertEqual(['#','-','1',' ','-','2',' ','-','3',' ','-','4',' ','-'], firstcol)

    def testStationNames(self):
        """Station names should be "Basel SBB" and "Zürich HB"."""
        self.assertTrue(self.rows[2].startswith('1  | Basel SBB'))
        self.assertTrue(self.rows[3].startswith('   | Zürich HB'))


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
        jobs = [gevent.spawn(envoy.run, '%s %s' % (BASE_COMMAND, arg)) for arg in args]
        gevent.joinall(jobs, timeout=10, raise_error=False)

        statuscodes = [job.value.status_code for job in jobs]
        self.assertEqual([0, 0, 0], statuscodes)

        stdout_values = [job.value.std_out for job in jobs]
        self.assertTrue(stdout_values[1:] == stdout_values[:-1])


if __name__ == '__main__':
    unittest.main()
