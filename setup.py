#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='falcons_nest',
    version='0.0.1',
    description='Light weight REST API framework based on falcon and gevent',
    author='Gregory Knight',
    packages=['falcons_nest'],
    install_requires=['falcon>=0.1.9', 'gevent>=1.0.1', 'daemonize>=2.3.1', 'lockfile>=0.10.2'],
    entry_points = {
        "console_scripts": ["falcons_nest = falcons_nest.command_line:main"],
    },
)

if __name__ == '__main__':
    pass
