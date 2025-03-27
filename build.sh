#!/usr/bin/env bash
# Exit on error
set -o errexit

#modify this line as neede for your package manager (pip , poetry, etc)
pip install -r requirements.txt

#Convet static assets files
python manage.py collectstatic --no-inputs

# Apply any outstanding database migration
python manage.py migrate