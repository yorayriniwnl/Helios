# Simple Dockerfile for Helios backend
# Uses official Python slim image, installs requirements, and runs uvicorn

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Allow build-time override of environment (default to production for images used in deploy)
ARG ENV=production
ENV ENV=${ENV}
ENV HELIOS_ENV=${ENV}
ENV LOG_LEVEL=INFO
ENV PORT=8000

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the app port (expand at build time)
EXPOSE ${PORT}

# Run the FastAPI app with Uvicorn. Use shell form so env vars are expanded.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL}"]
