#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# CRITICAL: Collect static files
echo "Running Collectstatic..."
python manage.py collectstatic --no-input --clear

# Apply migrations
python manage.py migrate
