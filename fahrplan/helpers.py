# -*- coding: utf-8 -*-

# Helper function to print directly to sys.stderr
from __future__ import print_function
from functools import partial
import sys
perror = partial(print, file=sys.stderr)
