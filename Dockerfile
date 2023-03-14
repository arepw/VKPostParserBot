# Use slim-buster varian of the Python image to reduce the size of the final image
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install required dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install supervisor and create configuration file
RUN apt-get update && \
    apt-get install -y supervisor && \
    mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start supervisord
CMD ["/usr/bin/supervisord", "-n"]
