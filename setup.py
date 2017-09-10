#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
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
      url=meta.url,
      packages=['fahrplan'],
      zip_safe=False,
      include_package_data=True,
      license=meta.license,
      keywords=meta.keywords,
      long_description=readme,
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              '%s = fahrplan.main:main' % meta.title,
          ]
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Natural Language :: German',
          'Natural Language :: French',
          'Natural Language :: Italian',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet',
          'Topic :: Terminals',
      ],
)
