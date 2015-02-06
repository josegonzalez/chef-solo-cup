#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chef_solo_cup import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='chef-solo-cup',
    version=__version__,
    author='Jose Diaz-Gonzalez',
    author_email='email@josediazgonzalez.com',
    packages=['chef_solo_cup', 'chef_solo_cup.commands'],
    scripts=['bin/chef-solo-cup'],
    url='https://github.com/josegonzalez/chef-solo-cup',
    license=open('LICENSE.txt').read(),
    classifiers=[
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    description='Chef-Solo wrapper',
    long_description=open('README.rst').read(),
    install_requires=open('requirements.txt').readlines(),
)
