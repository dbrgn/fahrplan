import unittest
import envoy
from .context import fahrplan


BASE_COMMAND = 'python fahrplan/main.py'


class TestBasicArgumentHandling(unittest.TestCase):

    def testTooFewArguments(self):
        args = ['', '-i', '-d']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertEqual('Not enough arguments.\n', r.std_err)

    def testVersionInfo(self):
        args = ['-v', '--version']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertEqual('%s %s\n' % (fahrplan.meta.title, fahrplan.meta.version), r.std_out)

    def testHelp(self):
        args = ['-h', '--help']
        for arg in args:
            r = envoy.run('%s %s' % (BASE_COMMAND, arg))
            self.assertIn('%s: %s' % (fahrplan.meta.title, fahrplan.meta.description), r.std_out)
            self.assertIn('Usage:', r.std_out)
            self.assertIn('Options:', r.std_out)
            self.assertIn('Arguments:', r.std_out)
            self.assertIn('Examples:', r.std_out)

if __name__ == '__main__':
    unittest.main()
