#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import fahrplan

f = open('requirements.txt', 'r')
lines = f.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]
readme = open('README.md').read()

setup(name='fahrplan',
      version=fahrplan.meta.version,
      description=fahrplan.meta.description,
      author=fahrplan.meta.author,
      author_email=fahrplan.meta.author_email,
      url='https://github.com/gwrtheyrn/fahrplan.py',
      packages=find_packages(),
      zip_save=False,
      include_package_data=True,
      license=fahrplan.meta.license,
      keywords='fahrplan timetable sbb cff ffs public transport',
      long_description=readme,
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              '%s = fahrplan.main:main' % fahrplan.meta.title,
          ]
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Natural Language :: German',
          'Natural Language :: French',
          'Natural Language :: Italian',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet',
          'Topic :: Terminals',
      ],
)
