# Use influxdb CLI for initialization
FROM influxdb:2

# Install curl for health check
RUN apt-get update && apt-get install -y curl

WORKDIR /app

# Copy initialization script
COPY init-buckets.sh .
RUN chmod +x init-buckets.sh

CMD ["./init-buckets.sh"]
