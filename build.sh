#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create upload directories
mkdir -p static/uploads/videos
mkdir -p static/uploads/audio

# Run database migrations
flask db upgrade

# Seed database if needed
flask seed-db || true
