# Builder stage
FROM python:3.10-alpine as builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    postgresql-dev \
    python3-dev \
    libpq

# Create a virtual environment
RUN python -m venv /opt/venv
# Ensure we use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Final stage
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies (no-cache to keep image small)
RUN apk add --no-cache libpq

# Create a non-root user and group for security
RUN addgroup -S django && adduser -S django -G django

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Change ownership of the application code
RUN chown -R django:django /app

# Switch to non-root user
USER django

EXPOSE 8000

# Run migrations and start the application
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 backend_pti.wsgi"]sgi"]
EXPOSE 8000