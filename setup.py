#!/usr/bin/env python

from distutils.core import setup

setup(name='netMon',
      version='0.1',
      description='Distributed Network Monitoring',
      author='Mathijs Mortimer',
      author_email='mathijs@mortimer.nl',
      url='https://github.com/thiezn/netMon',
      packages=['netMon'],
      install_requires=[
          'Twisted==15.2.1'
          ]
      )
