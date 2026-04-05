#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static assets (for Swagger UI styles)
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Seed the database, for the first deploy
python seed_db.py
