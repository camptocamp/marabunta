# -*- coding: utf-8 -*-

import re

from setuptools import setup, find_packages

with open('marabunta/core.py') as f:
    version = re.search('^__version__\s*=\s*"(.*)"', f.read(), re.M).group(1)
with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(
    name='marabunta',
    version=version,
    description='Migration tool for Odoo',
    long_description=readme + '\n\n' + history,
    author='Camptocamp (Guewen Baconnier)',
    author_email='guewen.baconnier@camptocamp.com',
    url='https://github.com/camptocamp/marabunta',
    license='AGPLv3+',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=["psycopg2",
                      "PyYAML",
                      "pexpect",
                      ],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    entry_points={
        'console_scripts': ['marabunta = marabunta.core:main']
    },
)
