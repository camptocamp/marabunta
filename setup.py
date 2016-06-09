# -*- coding: utf-8 -*-

import re

from setuptools import setup, find_packages

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('marabunta/core.py').read(),
    re.M
    ).group(1)

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='marabunta',
    version=version,
    description='Migration tool for Odoo',
    long_description=readme,
    author='Camptocamp (Guewen Baconnier)',
    author_email='guewen.baconnier@camptocamp.com',
    url='https://github.com/camptocamp/marabunta',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=["psycopg2",
                      "PyYAML"],
    entry_points={
        'console_scripts': ['marabunta = marabunta.core:main']
    },
)
