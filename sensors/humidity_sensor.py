from base_sensor import BaseSensor
import random
import math
import time

class HumiditySensor(BaseSensor):
    def __init__(self, sensorId, location, min_value=30.0, max_value=80.0, interval=5):
        super().__init__(
            sensorId=sensorId,
            sensorType="humidity",
            location=location,
            unit="%",
            min_value=min_value,
            max_value=max_value,
            interval=interval
        )
        
    async def generate_reading(self):
        """Generate a realistic humidity reading with some variation over time."""
        # Add a bit of realism by simulating humidity fluctuations
        current_time = int(time.time())
        # Adding a sine wave pattern to simulate daily humidity changes
        time_factor = (current_time % 86400) / 86400  # Position in the day (0-1)
        # Humidity is often inverse to temperature - higher at night, lower during the day
        day_night_factor = 0.5 * (self.max_value - self.min_value) * (
            0.5 - 0.5 * math.sin(2 * math.pi * time_factor - math.pi / 2)
        )
        
        # Add some random noise
        noise = random.uniform(-2.0, 2.0)
        
        # Calculate final humidity
        humidity = self.min_value + day_night_factor + noise
        
        return round(min(max(humidity, self.min_value), self.max_value), 2)
