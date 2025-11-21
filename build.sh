#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# CRITICAL: Collect static files into one folder for WhiteNoise
echo "Collecting Static Files..."
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
