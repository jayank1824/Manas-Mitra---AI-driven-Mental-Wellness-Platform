#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Ensure data and upload directories exist
mkdir -p data
mkdir -p app/static/uploads

# Seed database with initial questions, activities, and communities
python -m data.seed_data
