FROM python:3.12.6-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


FROM python:3.12.6-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -r appuser

# Set working directory
WORKDIR /app

# Copy Python packages and app from builder
COPY --from=builder /usr/local /usr/local

# Copy project files and set ownership
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Ensure entrypoint script is executable
RUN chmod +x /app/entrypoint.prod.sh

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Start app with entrypoint script
CMD ["/app/entrypoint.prod.sh"]
