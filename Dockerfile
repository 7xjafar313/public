FROM python:3.10-slim

# Install system dependencies (FFmpeg for merging, curl & unzip to install Deno JS runtime)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && curl -fsSL https://deno.land/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Add Deno to system PATH for yt-dlp to find it
ENV PATH="/root/.deno/bin:$PATH"

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Render sets PORT environment variable, we will run a dummy server on it)
EXPOSE 8000

# Start command
CMD ["python", "bot.py"]
