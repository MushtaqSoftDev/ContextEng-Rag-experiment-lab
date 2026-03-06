# Root Dockerfile for Railway, Render, Fly.io, etc.
# Single container: nginx (frontend) + uvicorn (backend)

# Stage 1: Build frontend
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Backend + runtime
FROM python:3.11-slim

WORKDIR /app

ENV TORCH_CUDA_ARCH_LIST=""
ENV PYTORCH_CUDA_ALLOC_CONF=""

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir -p /app/uploads /app/storage

# Frontend static files
COPY --from=frontend /app/dist /usr/share/nginx/html

# Nginx: serve frontend + proxy /api and /health to uvicorn (port replaced at runtime via start.sh)
RUN echo 'server { \
    listen 0.0.0.0:80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location /health { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_connect_timeout 5s; \
        proxy_read_timeout 5s; \
    } \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_buffering off; \
        proxy_read_timeout 300s; \
    } \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/sites-available/default

EXPOSE 80

COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
