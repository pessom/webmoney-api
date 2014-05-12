#!/usr/bin/env python

from setuptools import setup

requires = ["lxml",
            "xmltodict",
            "requests"]

setup(name='webmoney-api',
      version='0.0.2',
      description='Wrapper for webmoney interfaces',
      author='Stas Kaledin',
      author_email='staskaledin@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      packages=['webmoney_api'],
      install_requires=requires
      )
