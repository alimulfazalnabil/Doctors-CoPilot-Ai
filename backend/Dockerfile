# ==========================================
# STAGE 1: Build static FFmpeg and dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install basic system utilities for downloading and extracting binaries
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Download John Van Sickle's official static release build of FFmpeg for amd64
RUN wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar -xf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-amd64-static ffmpeg-static

# ==========================================
# STAGE 2: Build Python Virtual Environment
# ==========================================
FROM python:3.11-slim AS python-builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 3: Final Production Runtime (Secure & Non-Root)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Install minimal runtime libraries required by Python packages or media handling
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from python-builder stage
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy static FFmpeg and FFprobe binaries from builder stage
COPY --from=builder /build/ffmpeg-static/ffmpeg /usr/local/bin/ffmpeg
COPY --from=builder /build/ffmpeg-static/ffprobe /usr/local/bin/ffprobe

# Copy application source code
COPY ./app ./app

# Create a non-privileged system user for zero-trust security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health/live')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
