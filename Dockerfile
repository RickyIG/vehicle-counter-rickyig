# Gunakan image resmi dari Ultralytics
FROM ultralytics/ultralytics:8.3.135-cpu

# Set working directory di dalam container
WORKDIR /app

# Install ffmpeg dan lib tambahan jika belum ada
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements tambahan (jika ada)
COPY requirements.txt .

# Install Python dependencies tambahan (selain yg sudah ada di base image)
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh source code ke container
COPY . .

# Default environment variable untuk RTSP URL
ENV RTSP_URL=rtsp://host.docker.internal:8554/mystream

# Default command menjalankan script dengan argumen --rtsp_url dari env
CMD ["python", "vehicle_counter.py", "--rtsp_url", "${RTSP_URL}"]
