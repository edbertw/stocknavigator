# Stage 1: Build React frontend
FROM node:18-alpine AS react-build

WORKDIR /app
COPY client/package.json client/package-lock.json ./
RUN npm install

COPY client/ ./
# Fix: Use proper environment variable syntax and handle build errors
RUN npm run build

# Stage 2: Build Django backend
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY server/ .

# Copy React static files from Stage 1
COPY --from=react-build /app/build /app/server/static/frontend

# The command will be overridden by docker-compose
ENV DJANGO_SETTINGS_MODULE=mybackend.settings
CMD ["sh", "-c", "${DJANGO_CMD:-python manage.py runserver 0.0.0.0:8000}"]