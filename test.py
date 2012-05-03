import unittest
import envoy

class TestBasicArgumentHandling(unittest.TestCase):

    def testUsageInfo(self):
        """Test whether the usage info is shown if there are no parameters
        defined."""
        r = envoy.run('python fahrplan/main.py')
        self.assertIn('usage: fahrplan', r.std_err)

    def testTooFewArguments(self):
        r0 = envoy.run('python fahrplan/main.py')
        r1 = envoy.run('python fahrplan/main.py foo')
        self.assertIn('error: too few arguments', r0.std_err)
        self.assertIn('error: too few arguments', r1.std_err)


if __name__ == '__main__':
    unittest.main()
