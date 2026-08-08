#!/usr/bin/env bash
# exit on error
set -o errexit

# Move into Django app dir
cd reviewai

# Run database migrations
python manage.py migrate

# Seed the database with the E-Commerce, Restaurant, and Hospitality demo reviews
python manage.py seed_demo_data

# Start Gunicorn server
gunicorn config.wsgi:application
