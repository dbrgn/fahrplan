# -*- coding: utf-8 -*-
import functools
import sys


# Helper function to print directly to sys.stderr
perror = functools.partial(print, file=sys.stderr)
