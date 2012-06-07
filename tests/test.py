import unittest
import envoy
from .context import fahrplan

class TestBasicArgumentHandling(unittest.TestCase):

    def testTooFewArguments(self):
        args = ['', '-i', '-d']
        for arg in args:
            r = envoy.run('python fahrplan/main.py %s' % arg)
            self.assertEqual('Not enough arguments.\n', r.std_err)

if __name__ == '__main__':
    unittest.main()
