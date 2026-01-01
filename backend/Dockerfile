FROM python:3.10-slim

# 1.5. Prevent Python from buffering stdout/stderr (Instant logs in Cloud Run)
ENV PYTHONUNBUFFERED=1

# 2. Install system dependencies (ESSENTIAL for audio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Setup working directory
WORKDIR /app

# 4. Create a non-root user
RUN useradd -m -u 1000 user

# 5. Create necessary data directories (as root) and fix permissions
RUN mkdir -p data/downloads data/stems data/exports && \
    chown -R user:user /app

# 6. Copy requirements and install (as root for global pip, or user)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 7. Switch to non-root user for security
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# 8. Copy the rest of your application and ensure ownership
COPY --chown=user . .

# 9. Expose the port
EXPOSE 8080

# 8. Start the FastAPI server
# Using the --port flag with $PORT ensures Cloud Run compatibility
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]