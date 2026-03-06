#!/bin/bash
set -e

# Railway/Render inject PORT; default 80 for local
LISTEN_PORT="${PORT:-80}"
sed -i "s/listen 0.0.0.0:80/listen 0.0.0.0:$LISTEN_PORT/" /etc/nginx/sites-available/default

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
exec nginx -g "daemon off;"
