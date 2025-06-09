FROM python:3.12.6-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12.6-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000 

# Make entry file executable
RUN chmod +x  /app/entrypoint.prod.sh
 
# Start the application using Gunicorn
CMD ["/app/entrypoint.prod.sh"]
