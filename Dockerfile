# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y build-essential libssl-dev && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for certificates
RUN mkdir -p /app/web4_certs

# Copy entrypoint script
COPY start.sh .

# Make it executable
RUN chmod +x start.sh

# Run entrypoint script
ENTRYPOINT ["./start.sh"]
