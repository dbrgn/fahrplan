import unittest2 as unittest
import envoy
import fahrplan


BASE_COMMAND = 'python fahrplan/main.py'


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
            self.assertEqual('%s %s\n' % (fahrplan.meta.title, fahrplan.meta.version), r.std_out)

    def testHelp(self):
        args = ['-h', '--help']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertTrue('%s: %s' % (fahrplan.meta.title, fahrplan.meta.description) in r.std_out)
            self.assertTrue('Usage:' in r.std_out)
            self.assertTrue('Options:' in r.std_out)
            self.assertTrue('Arguments:' in r.std_out)
            self.assertTrue('Examples:' in r.std_out)


class TestInputParsing(unittest.TestCase):

    valid_expected_result = {'arrival': '19:00', 'departure': '18:00', 'from': 'Zürich', 'to': 'Locarno', 'via': 'Genève'}

    def testEmptyArguments(self):
        tokens = []
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneValidArgument(self):
        tokens = ['from']
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testOneInvalidArgument(self):
        tokens = ['foobar']
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual({}, data)
        self.assertIsNone(language)

    def testValidArgumentsEn(self):
        tokens = ['from', 'Zürich', 'to', 'Locarno', 'via', 'Genève', 'departure', '18:00', 'arrival', '19:00']
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('en', language)

    def testValidArgumentsDe(self):
        tokens = ['von', 'Zürich', 'nach', 'Locarno', 'via', 'Genève', 'ab', '18:00', 'an', '19:00']
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('de', language)

    def testValidArgumentsFr(self):
        tokens = ['de', 'Zürich', 'à', 'Locarno', 'via', 'Genève', 'départ', '18:00', 'arrivée', '19:00']
        data, language = fahrplan.main.parse_input(tokens)
        self.assertEqual(self.valid_expected_result, data)
        self.assertEqual('fr', language)

    def testNotEnoughArgument(self):
        tokens = ['from', 'basel', 'via', 'bern']
        self.assertRaises(ValueError, fahrplan.main.parse_input, tokens)


if __name__ == '__main__':
    unittest.main()
