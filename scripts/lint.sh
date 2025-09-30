#!/usr/bin/env bash

set -ex

echo "Running black..."
python3 -m black src
python3 -m black tests

echo "Running isort..."
python3 -m isort src
python3 -m isort tests

echo "Running flake8..."
python3 -m flake8 --show-source --statistics --config=setup.cfg src
python3 -m flake8 --show-source --statistics --config=setup.cfg tests

echo "Running mypy..."
mypy src
MYPYPATH=src mypy tests