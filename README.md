fahrplan.py
===========

[![Build Status](https://secure.travis-ci.org/gwrtheyrn/fahrplan.py.png?branch=master)](http://travis-ci.org/gwrtheyrn/fahrplan.py)

*Work in progress, still very hackish code!*

Goal: Simple access to the sbb timetable service from the commandline.

Relies on the public transport API by opendata.ch: http://transport.opendata.ch/


Installing
----------

To install current development version using pip, issue:

    $ sudo pip install -e git://github.com/gwrtheyrn/fahrplan.py.git#egg=fahrplan-dev

![Screenshot](http://make.opendata.ch/lib/exe/fetch.php?media=project:20120331_160821.png)


Testing
-------

To run the tests, run the following command from the root folder:

    python -m tests.test

If you have fabric installed, you can also use the `test` command:

   fab test
