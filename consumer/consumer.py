import asyncio
import json
import os
import logging
import nats
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("consumer")

class DataConsumer:
    def __init__(self):
        # InfluxDB configuration
        self.influx_url = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
        self.influx_token = os.environ.get("INFLUXDB_TOKEN", "")
        self.influx_org = os.environ.get("INFLUXDB_ORG", "acme_corp")
        self.influx_bucket = os.environ.get("INFLUXDB_BUCKET", "the_bucket")
        
        # NATS configuration
        self.nats_url = os.environ.get("NATS_URL", "nats://nats:4222")
        
        # Initialize clients
        self.influx_client = None
        self.write_api = None
        self.nats_conn = None

    async def setup(self):
        """Set up connections to InfluxDB and NATS."""
        # Connect to InfluxDB
        logger.info(f"Connecting to InfluxDB at {self.influx_url}")
        logger.info(f"InfluxDB token: {self.influx_token}")
        self.influx_client = InfluxDBClient(
            url=self.influx_url,
            token=self.influx_token,
            org=self.influx_org
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
        # Connect to NATS
        logger.info(f"Connecting to NATS at {self.nats_url}")
        self.nats_conn = await nats.connect(self.nats_url)
        
        logger.info("Consumer setup complete")

    def store_data(self, data):
        """Store data in InfluxDB."""
        try:
            # Create a point with the sensor data
            point = Point(data["sensor_type"]) \
                .tag("sensor_id", data["sensor_id"]) \
                .tag("location", data["location"]) \
                .field("value", data["value"]) \
                .time(data["timestamp"])
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.influx_bucket, record=point)
            logger.info(f"Stored data for {data['sensor_type']} sensor {data['sensor_id']}")
        except Exception as e:
            logger.error(f"Error storing data: {e}")

    async def message_handler(self, msg):
        """Handle incoming NATS messages."""
        try:
            # Decode and parse the message
            data = json.loads(msg.data.decode())
            logger.info(f"Received message: {data}")
            
            # Store the data in InfluxDB
            self.store_data(data)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {msg.data}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def subscribe_to_sensors(self):
        """Subscribe to all sensor topics."""
        try:
            # Subscribe to all sensor data
            await self.nats_conn.subscribe("sensors.>", cb=self.message_handler)
            logger.info("Subscribed to all sensor topics")
        except Exception as e:
            logger.error(f"Error subscribing to topics: {e}")

    async def run(self):
        """Run the consumer service."""
        try:
            await self.setup()
            await self.subscribe_to_sensors()
            
            # Keep the service running
            while True:
                await asyncio.sleep(3600)  # Just keep the service alive
        except Exception as e:
            logger.error(f"Error in consumer service: {e}")
        finally:
            # Clean up resources
            if self.influx_client:
                self.influx_client.close()
            if self.nats_conn:
                await self.nats_conn.close()

async def main():
    consumer = DataConsumer()
    await consumer.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer service stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
