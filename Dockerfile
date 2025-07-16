# IBM ACP Agent Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r acpuser && useradd -r -g acpuser acpuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/acpuser/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs temp examples && \
    chown -R acpuser:acpuser /app

# Switch to non-root user
USER acpuser

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/acp/health')" || exit 1

# Default command
CMD ["python", "main.py"] 