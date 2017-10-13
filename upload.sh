#!/bin/sh

rm -rf dist/

python setup.py sdist
twine upload dist/*

rm -rf dist/
rm -rf jojo.egg-info/
