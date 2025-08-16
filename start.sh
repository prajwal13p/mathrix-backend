#!/bin/bash

# Production startup script for Mathrix API

echo "🚀 Starting Mathrix API..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import time
import psycopg2
from app.core.config import settings

while True:
    try:
        conn = psycopg2.connect(settings.database_url)
        conn.close()
        print('✅ Database connection successful!')
        break
    except Exception as e:
        print(f'⏳ Waiting for database... {e}')
        time.sleep(5)
"

# Run database migrations
echo "🔧 Running database migrations..."
alembic upgrade head

# Start the application
echo "🌟 Starting FastAPI application..."
if [ "$DEBUG" = "true" ]; then
    echo "🐛 Debug mode enabled"
    uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
else
    echo "🚀 Production mode"
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
fi
