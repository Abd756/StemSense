# 1. Use an official Python runtime with a good base
FROM python:3.10-slim

# 2. Install system dependencies (ESSENTIAL for audio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Create a working directory and a non-root user (Required by HF)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# 4. Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 5. Copy the rest of your application
COPY --chown=user . .

# 6. Create necessary data directories with permissions
RUN mkdir -p data/downloads data/stems data/exports

# 7. Expose the port (Cloud Run uses 8080 by default)
EXPOSE 8080

# 8. Start the FastAPI server
# Using the --port flag with $PORT ensures Cloud Run compatibility
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]