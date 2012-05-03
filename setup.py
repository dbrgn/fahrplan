from setuptools import setup, find_packages
from fahrplan import __version__ as version

setup(
    name = 'fahrplan',
    version = version,
    description = 'A SBB/CFF/FFS commandline based timetable client. Work in progress at makeopendata.ch.',
    author = 'Danilo Bargen',
    author_email = '',
    url = 'https://github.com/gwrtheyrn/fahrplan.py',
    packages = find_packages(),
    zip_safe=False,
    include_package_data = True,
    install_requires=[
        'requests',
        'envoy',
        'python-dateutil',
    ],
    classifiers = [ # TODO: Add more, e.g. license etc.
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    entry_points={
        'console_scripts': [
            'fahrplan = fahrplan.main:main',
        ]
    },
)