#!/usr/bin/env python

# Copyright (C) 2017 SignalFx, Inc. All rights reserved.

from setuptools import setup, find_packages

with open('signalfx_lambda/version.py') as f:
    exec(f.read())

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name=name,  # noqa
    version=version,  # noqa
    author='SignalFx, Inc',
    author_email='info@signalfx.com',
    description='SignalFx Lambda Python Wrapper',
    license='Apache Software License v2',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    zip_safe=True,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url='https://github.com/signalfx/lambda-python',
)
