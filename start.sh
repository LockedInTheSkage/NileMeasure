#!/bin/bash

echo "Starting sensor data simulation system..."
echo "This will start NATS, InfluxDB, sensors, consumer, processor, alert, and GraphQL services."
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

# Check if the .env file exists
if [ ! -f ".env" ]; then
  echo "Warning: .env file not found. Creating a sample .env file with random credentials."
  echo "Please review the file and modify if needed before continuing."
  
  # Generate random password and token
  RANDOM_PASSWORD=$(openssl rand -hex 16)
  RANDOM_TOKEN=$(openssl rand -base64 64)
  
  cat > .env << EOF
# InfluxDB Configuration
INFLUXDB_ADMIN_USERNAME=admin
INFLUXDB_ADMIN_PASSWORD=$RANDOM_PASSWORD
INFLUXDB_ORG=acme_corp
INFLUXDB_BUCKET=sensor_data
INFLUXDB_AGGREGATED_BUCKET=aggregated_data
INFLUXDB_ADMIN_TOKEN=$RANDOM_TOKEN

# Alert Configuration
TEMP_ALERT_THRESHOLD=30.0
EOF
  
  echo "Sample .env file created with the following credentials:"
  echo "Username: admin"
  echo "Password: $RANDOM_PASSWORD"
  echo "Token: $RANDOM_TOKEN"
  echo "These credentials are stored in the .env file."
  echo "Note: You'll need these credentials to access the InfluxDB UI."
  echo "Press Enter to continue or Ctrl+C to abort and modify the file."
  read
fi

# Check if email config file exists
if [ ! -f "alert/config/email_config.json" ]; then
  if [ -f "alert/config/email_config.sample.json" ]; then
    echo "Warning: email_config.json not found. Creating from template."
    cp alert/config/email_config.sample.json alert/config/email_config.json
    echo "Created email_config.json from template."
    echo "Please update the email settings in alert/config/email_config.json before using the alert service."
    echo "Press Enter to continue or Ctrl+C to abort and modify the file."
    read
  else
    echo "Warning: Neither email_config.json nor email_config.sample.json found."
    echo "The email alert service may not function correctly."
  fi
fi

echo "Building and starting services..."
docker compose -f 2025-05-12-junior-backend-cloud-docker-compose.yaml up -d --build --force-recreate

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
