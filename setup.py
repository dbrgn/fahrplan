#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from fahrplan import meta

f = open('requirements.txt', 'r')
lines = f.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]
readme = open('README.rst').read()

setup(name='fahrplan',
      version=meta.version,
      description=meta.description,
      author=meta.author,
      author_email=meta.author_email,
      url='https://github.com/dbrgn/fahrplan',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      license=meta.license,
      keywords='fahrplan timetable sbb cff ffs public transport',
      long_description=readme,
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              '%s = fahrplan.main:main' % meta.title,
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Natural Language :: German',
          'Natural Language :: French',
          'Natural Language :: Italian',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet',
          'Topic :: Terminals',
      ],
)
