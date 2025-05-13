import asyncio
import json
import random
import time
from datetime import datetime
import nats
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseSensor:
    def __init__(self, sensor_id, sensor_type, location, unit, min_value, max_value, interval=5):
        """
        Initialize a base sensor.
        
        Args:
            sensor_id (str): Unique identifier for the sensor
            sensor_type (str): Type of the sensor (temperature, humidity, etc.)
            location (str): Location of the sensor
            unit (str): Unit of measurement
            min_value (float): Minimum value for the sensor
            max_value (float): Maximum value for the sensor
            interval (int): Interval in seconds between readings
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.interval = interval
        self.logger = logging.getLogger(f"{sensor_type}_{sensor_id}")

    async def generate_reading(self):
        """Generate a random reading within the specified range."""
        return round(random.uniform(self.min_value, self.max_value), 2)

    def format_reading(self, value):
        """Format the reading as a JSON string."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        data = {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "location": self.location,
            "value": value,
            "unit": self.unit,
            "timestamp": timestamp
        }
        return json.dumps(data)

    async def publish_reading(self, nc, value):
        """Publish a reading to NATS."""
        subject = f"sensors.{self.sensor_type}.{self.sensor_id}"
        message = self.format_reading(value)
        await nc.publish(subject, message.encode())
        self.logger.info(f"Published: {message}")

    async def run(self, nc):
        """Run the sensor, generating and publishing readings at regular intervals."""
        self.logger.info(f"Starting {self.sensor_type} sensor {self.sensor_id} in {self.location}")
        try:
            while True:
                value = await self.generate_reading()
                await self.publish_reading(nc, value)
                await asyncio.sleep(self.interval)
        except Exception as e:
            self.logger.error(f"Error in sensor {self.sensor_id}: {e}")
            raise
