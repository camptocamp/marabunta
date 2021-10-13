# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

if (sys.version_info[:3] < (3, 0)):
    with open('README.rst') as f:
        readme = f.read()
else:
    with open('README.rst', encoding='utf-8') as f:
        readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

test_deps = [
    "pytest",
    "mock",
]

extras = {
    'test': test_deps,
}

setup(
    name='marabunta',
    use_scm_version=True,
    description='Migration tool for Odoo',
    long_description=readme + '\n\n' + history,
    author='Camptocamp (Guewen Baconnier)',
    author_email='guewen.baconnier@camptocamp.com',
    url='https://github.com/camptocamp/marabunta',
    license='AGPLv3+',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "psycopg2",
        "ruamel.yaml>=0.15.1",
        "pexpect",
        "werkzeug",
        "future",
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    tests_require=test_deps,
    extras_require=extras,
    include_package_data=True,
    package_data={
        'marabunta': ['html/*.html'],
    },
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    entry_points={
        'console_scripts': ['marabunta = marabunta.core:main']
    },
)
