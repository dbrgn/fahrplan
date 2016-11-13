# -*- coding: utf-8 -*-
from __future__ import print_function

import functools
import sys


# Helper function to print directly to sys.stderr
perror = functools.partial(print, file=sys.stderr)
