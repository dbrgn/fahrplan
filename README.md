fahrplan.py
===========

[![Build Status](https://secure.travis-ci.org/gwrtheyrn/fahrplan.py.png?branch=master)](http://travis-ci.org/gwrtheyrn/fahrplan.py)

*Work in progress, still very hackish code!*

Goal: Simple access to the sbb timetable service from the commandline with human
readable argument parsing.

Relies on the public transport API by opendata.ch: http://transport.opendata.ch/


Installing
----------

To install current development version using pip, issue:

    $ sudo pip install -e git://github.com/gwrtheyrn/fahrplan.py.git#egg=fahrplan-dev


Usage
-----

`fahrplan --help`:

    Usage:
     %s [options] arguments

    Options:
     -v, --version Show version number
     -i, --info    Verbose output
     -d, --debug   Debug output
     -h, --help    Show this help

    Arguments:
     You can use natural language arguments using the following
     keywords in your desired language:
     en -- from, to, via, departure, arrival
     de -- von, nach, via, ab, an
     fr -- de, à, via, départ, arrivée

    Examples:
     fahrplan from thun to burgdorf
     fahrplan via bern nach basel von zürich, helvetiaplatz ab 15:35

![Screenshot](http://make.opendata.ch/lib/exe/fetch.php?media=project:20120331_160821.png)


Testing
-------

To run the tests, run the following command from the root folder:

    python -m tests.test

If you have fabric installed, you can also use the `test` command:

    fab test
