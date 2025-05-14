#!/bin/bash
# Wait for InfluxDB to be ready
echo "Waiting for InfluxDB to be ready..."
until curl -s http://influxdb:8086/ping > /dev/null; do
    sleep 1
done
echo "InfluxDB is ready"

# Create the aggregated_data bucket
echo "Creating aggregated_data bucket..."
influx bucket create \
  --name aggregated_data \
  --org acme_corp \
  --token $INFLUXDB_TOKEN \
  --host http://influxdb:8086

echo "Bucket setup complete"
