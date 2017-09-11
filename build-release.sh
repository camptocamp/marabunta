#!/bin/bash

python setup.py bdist bdist_wheel
twine upload --skip-existing dist/*
