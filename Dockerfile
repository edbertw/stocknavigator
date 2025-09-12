# Stage 1: Build React frontend
FROM node:18-alpine AS react-build

WORKDIR /app
ENV NODE_ENV=production
COPY client/package.json client/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY client/ ./
# Avoid CRA failing the build on warnings under CI
RUN CI= npm run build

# Stage 2: Build Django backend
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including psycopg2-binary for Python 3.11)
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary python-dotenv gunicorn

# Copy Django project
COPY server/ .

# Copy React static files from Stage 1
COPY --from=react-build /app/build /app/server/static/frontend

# The command will be overridden by docker-compose
# The default command can be overridden by docker-compose via DJANGO_CMD
ENV DJANGO_SETTINGS_MODULE=mybackend.settings
CMD ["sh", "-c", "${DJANGO_CMD:-python manage.py runserver 0.0.0.0:8000}"]
#CMD sh -c "gunicorn --bind 0.0.0.0:8000 \
    #--workers ${GUNICORN_WORKERS} \
    #--threads ${GUNICORN_THREADS} \
    #--timeout ${GUNICORN_TIMEOUT} \
    #--worker-class sync \
    #mybackend.wsgi:application"