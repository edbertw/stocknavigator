# Stage 1: Build React frontend
FROM node:18-alpine as react-build

WORKDIR /app
COPY myfrontend/package.json myfrontend/package-lock.json ./
RUN npm install

COPY myfrontend/ ./
RUN npm run build  # Outputs to /app/build

# Stage 2: Build Django backend
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system dependencies (for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY mybackend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Django project
COPY mybackend/ .

# Copy React static files from Stage 1
COPY --from=react-build /app/build /app/mybackend/static/frontend

# Collect static files (Django)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Django with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mybackend.wsgi:application"]