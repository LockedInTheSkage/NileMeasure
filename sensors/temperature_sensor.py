from base_sensor import BaseSensor
import math
import time
import random

class TemperatureSensor(BaseSensor):
    def __init__(self, sensor_id, location, min_value=10.0, max_value=35.0, interval=5):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="temperature",
            location=location,
            unit="°C",
            min_value=min_value,
            max_value=max_value,
            interval=interval
        )
        
    async def generate_reading(self):
        """Generate a realistic temperature reading with some variation over time."""
        # Add a bit of realism by simulating temperature fluctuations
        current_time = int(time.time())
        # Adding a sine wave pattern to simulate day/night temperature changes
        time_factor = (current_time % 86400) / 86400  # Position in the day (0-1)
        day_night_factor = 0.5 * (1 + self.max_value - self.min_value) * (
            0.5 + 0.5 * math.sin(2 * math.pi * time_factor - math.pi / 2)
        )
        
        # Add some random noise
        noise = random.uniform(-0.5, 0.5)
        
        # Calculate final temperature
        temperature = self.min_value + day_night_factor + noise
        
        return round(temperature, 2)
