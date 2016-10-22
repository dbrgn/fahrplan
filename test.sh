#!/bin/bash
tox
flake8 --ignore E501,E128,W503 fahrplan/*.py
