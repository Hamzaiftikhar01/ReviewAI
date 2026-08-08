#!/usr/bin/env bash
# exit on error
set -o errexit

# Install pip dependencies
pip install -r requirements.txt

# Move into Django app dir
cd reviewai

# Collect static files
python manage.py collectstatic --no-input
