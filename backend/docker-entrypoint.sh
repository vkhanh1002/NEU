#!/bin/sh
set -eu

UPLOAD_DIR=/app/data/attendance
mkdir -p "$UPLOAD_DIR"
if [ "$(stat -c '%u' "$UPLOAD_DIR")" != "$(id -u study)" ]; then
    chown -R study:study "$UPLOAD_DIR"
fi

exec su -s /bin/sh study -c 'alembic upgrade head && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000'
