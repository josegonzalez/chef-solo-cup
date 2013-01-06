#!/usr/bin/env python

from distutils.core import setup

setup(name='chef-solo-cup',
      version='0.0.1',
      description='Chef-Solo wrapper',
      author='Jose Diaz-Gonzalez',
      author_email='email@josediazgonzalez.com',
      url='https://github.com/josegonzalez/chef-solo-cup',
      scripts=['bin/chef-solo-cup'],
      install_requires=open('requirements.txt').readlines(),
      long_description=open('README.rst').read()
      )
