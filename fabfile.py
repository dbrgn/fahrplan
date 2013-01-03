# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals

from fabric.api import local

def test():
    local('python -m fahrplan.tests.test')
