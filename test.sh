#!/bin/bash
nosetests fahrplan.tests.test \
    --with-coverage \
    --cover-erase \
    --cover-package=fahrplan
