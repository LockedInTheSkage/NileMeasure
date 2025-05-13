#!/bin/bash

echo "Starting sensor data simulation system..."
echo "This will start NATS, InfluxDB, sensors, consumer, and GraphQL services."
echo 

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not installed. Please start Docker and try again."
  exit 1
fi

# Check if the compose file exists
if [ ! -f "2025-05-12-junior-backend-cloud-docker-compose.yaml" ]; then
  echo "Error: Docker Compose file not found."
  exit 1
fi

echo "Building and starting services..."
docker compose -f 2025-05-12-junior-backend-cloud-docker-compose.yaml up -d --build

if [ $? -eq 0 ]; then
  echo 
  echo "Services started successfully!"
  echo 
  echo "You can access the services at:"
  echo "- GraphQL UI: http://localhost:8000"
  echo "- InfluxDB UI: http://localhost:8086"
  echo "- NATS Monitoring: http://localhost:8222"
  echo 
  echo "To view logs, run: docker compose -f 2025-05-12-junior-backend-cloud-docker-compose.yaml logs -f"
  echo "To stop services, run: docker compose -f 2025-05-12-junior-backend-cloud-docker-compose.yaml down"
else
  echo "Error starting services. Please check the logs for more details."
fi
