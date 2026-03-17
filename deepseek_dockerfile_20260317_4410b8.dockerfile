# Use a stable Debian-based Python image
FROM python:3.10-slim-bookworm

# Install system dependencies required by the Zoom SDK
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-shm0 \
    libxcb-randr0 \
    libxcb-image0 \
    libxcb-util1 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libgl1 \
    libegl1 \
    libpulse0 \
    libasound2 \
    libglib2.0-0 \
    libgirepository-1.0-1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (if not already exists)
RUN id -u appuser &>/dev/null || useradd --create-home appuser

# Increase pip timeout to avoid read timeouts
ENV PIP_DEFAULT_TIMEOUT=120

# Copy requirements and install Python dependencies (cached in image)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Switch to non-root user
USER appuser

# Set the working directory
WORKDIR /app

# Copy the Zoom SDK into the container
COPY zoomsdk /app/zoomsdk

# Set environment variable for SDK path
ENV ZOOM_SDK_PATH=/app/zoomsdk