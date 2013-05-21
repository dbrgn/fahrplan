fahrplan
========

.. image:: https://secure.travis-ci.org/dbrgn/fahrplan.png?branch=master
    :alt: Build status
    :target: http://travis-ci.org/dbrgn/fahrplan

.. image:: https://coveralls.io/repos/dbrgn/fahrplan/badge.png
    :alt: Coverage status
    :target: https://coveralls.io/r/dbrgn/fahrplan

.. image:: https://pypip.in/d/fahrplan/badge.png
    :alt: PyPI download stats
    :target: https://crate.io/packages/fahrplan

Goal: Simple access to the sbb timetable service from the commandline with human
readable argument parsing.

Relies on the public transport API by opendata.ch: http://transport.opendata.ch/

Fahrplan support both Python 2.6 and 2.7. PyPy should be working (except for the
tests), but there is no official support until the tests are fixed. Python 3.3
support is under way.


Installing
----------

To install current version using pip, issue::

    $ sudo pip install fahrplan


Usage
-----

``fahrplan --help``::

    Usage:
     fahrplan [options] arguments

    Options:
     -f, --full    Show full connection info, including changes
     -i, --info    Verbose output
     -d, --debug   Debug output
     -v, --version Show version number
     -h, --help    Show this help

    Arguments:
     You can use natural language arguments using the following
     keywords in your desired language:
     en -- from, to, via, departure, arrival
     de -- von, nach, via, ab, an
     fr -- de, à, via, départ, arrivée

     You can also use natural time specifications in your language, like "now",
     "immediately", "noon" or "midnight".

    Examples:
     fahrplan from thun to burgdorf
     fahrplan via neuchâtel à lausanne de zurich, helvetiaplatz départ 15:35
     fahrplan von bern nach basel an um mitternacht

.. image:: https://raw.github.com/dbrgn/fahrplan/master/screenshot.png
    :alt: Screenshot


Testing
-------

Prior to testing, you should install the required libraries (preferrably in
a virtualenv)::

    $ virtualenv --no-site-packages VIRTUAL
    $ . VIRTUAL/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt

To run the test script::

    $ ./test.sh


Sourcecode
----------

The sourcecode is available on Github: https://github.com/dbrgn/fahrplan


License
-------

The code is licensed as GPLv3. See `LICENSE` file for more details.
