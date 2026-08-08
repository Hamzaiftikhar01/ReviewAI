#!/usr/bin/env bash
# exit on error
set -o errexit

# Install pip dependencies
pip install -r requirements.txt

# Move into Django app dir
cd reviewai

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Seed the database with the E-Commerce, Restaurant, and Hospitality demo reviews
python manage.py seed_demo_data
