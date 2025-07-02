# Stage 1: Build React frontend
FROM node:18-alpine as react-build

WORKDIR /app
COPY client/package.json client/package-lock.json ./
RUN npm install

COPY client/ ./
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
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including psycopg2-binary for Python 3.11)
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary python-dotenv

# Copy Django project
COPY server/ .

# Copy React static files from Stage 1
COPY --from=react-build /app/build /app/server/static/frontend

# The command will be overridden by docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD sh -c "gunicorn --bind 0.0.0.0:8000 \
    #--workers ${GUNICORN_WORKERS} \
    #--threads ${GUNICORN_THREADS} \
    #--timeout ${GUNICORN_TIMEOUT} \
    #--worker-class sync \
    #mybackend.wsgi:application"