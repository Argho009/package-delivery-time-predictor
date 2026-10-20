# ─────────────────────────────────────────────────────────────────
# DeliverAI: AI Package Delivery Time Prediction System
# Production Dockerfile for Hugging Face Spaces (100% Free 24/7 Hosting)
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PORT=7860 \
    FLASK_PORT=7860 \
    KMP_DUPLICATE_LIB_OK=TRUE \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    LOKY_MAX_CPU_COUNT=1

WORKDIR /app

# Install system dependencies needed for OpenMP, compilation & C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code, models, and static frontend assets
COPY . .

# Set up user 1000 required by Hugging Face Spaces
RUN useradd -m -u 1000 user && \
    chown -R user:user /app
USER user

EXPOSE 7860

# Run main.py which automatically binds to port 7860 on Hugging Face
CMD ["python", "main.py"]
