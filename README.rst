fahrplan
========

.. image:: https://img.shields.io/travis/dbrgn/fahrplan/master.svg
    :alt: Build status
    :target: http://travis-ci.org/dbrgn/fahrplan

.. image:: https://img.shields.io/coveralls/dbrgn/fahrplan/master.svg
    :alt: Coverage status
    :target: https://coveralls.io/r/dbrgn/fahrplan

Goal: Simple access to the SBB/CFF/FFS timetable service from the commandline with human
readable argument parsing.

Relies on the public transport API by opendata.ch: http://transport.opendata.ch/

Fahrplan supports Python 2.7 and 3.5. PyPy should be working (except for the
tests), but there is no official support until the tests are fixed.


Installing
----------

To install the current version using pip, issue::

    $ sudo pip install fahrplan

To install from this repository, clone it and use::

    $ python setup.py fahrplan

Usage
-----

``fahrplan --help``::

    usage: fahrplan [--full] [--info] [--debug] [--help] [--version]
		    [--proxy PROXY]
		    ...

    A SBB/CFF/FFS commandline based timetable client.

    positional arguments:
      request

    optional arguments:
      --full, -f            Show full connection info, including changes
      --info, -i            Verbose output
      --debug, -d           Debug output
      --help, -h            Show this help
      --version, -v         Show version number
      --proxy PROXY, -p PROXY
			    Use proxy for network connections (host:port)

    Arguments:
     You can use natural language arguments using the following
     keywords in your desired language:
     en -- from, to, via, departure, arrival
     de -- von, nach, via, ab, an
     fr -- de, à, via, départ, arrivée

     You can also use natural time and date specifications in your language, like
     - "now", "immediately", "at noon", "at midnight",
     - "tomorrow", "monday", "in 2 days", "22/11".

    Examples:
     fahrplan from thun to burgdorf
     fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35
     fahrplan de lausanne à vevey arrivée minuit
     fahrplan from Bern to Zurich departure 13:00 monday
     fahrplan -p proxy.mydomain.ch:8080 de lausanne à vevey arrivée minuit

.. image:: https://raw.github.com/dbrgn/fahrplan/master/screenshot.png
    :alt: Screenshot


Testing
-------

Testing is done using tox and nosetests.

To run the test script for Python 2 and 3::

    $ ./test.sh


Sourcecode
----------

The sourcecode is available on Github: https://github.com/dbrgn/fahrplan


License
-------

The code is licensed as GPLv3. See `LICENSE` file for more details.
