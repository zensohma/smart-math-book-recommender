#!/bin/sh
set -e

echo "Seeding database..."
python seed_db.py --reset --input ../data/processed/books_for_ml.csv

echo "Starting server..."
exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"
