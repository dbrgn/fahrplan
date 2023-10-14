#!/usr/bin/env bash
tox
flake8 --ignore E501,E128,W503,E711 fahrplan/*.py
