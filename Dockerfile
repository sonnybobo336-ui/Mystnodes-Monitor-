# Multi-stage build for production deployment
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend to backend static folder
COPY --from=frontend-builder /app/frontend/build ./backend/static

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run backend server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
