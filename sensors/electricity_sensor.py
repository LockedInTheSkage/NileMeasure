from base_sensor import BaseSensor
import random
import math
import time

class ElectricityUsageSensor(BaseSensor):
    def __init__(self, sensorId, location, min_value=0.1, max_value=5.0, interval=5):
        super().__init__(
            sensorId=sensorId,
            sensorType="electricity",
            location=location,
            unit="kW",
            min_value=min_value,
            max_value=max_value,
            interval=interval
        )
        self.base_usage = (min_value + max_value) / 2
        
    async def generate_reading(self):
        """Generate a realistic electricity usage reading with daily patterns."""
        current_time = int(time.time())
        
        # Get hour of the day (0-23)
        hour = (current_time % 86400) // 3600
        
        # Define usage patterns - higher in morning and evening
        if 7 <= hour < 9:  # Morning peak
            usage_factor = 0.7
        elif 17 <= hour < 22:  # Evening peak
            usage_factor = 0.9
        elif 22 <= hour < 24 or 0 <= hour < 6:  # Night (low usage)
            usage_factor = 0.3
        else:  # Regular daytime
            usage_factor = 0.5
            
        # Calculate the usage within our range based on the factor
        range_width = self.max_value - self.min_value
        base_value = self.min_value + (range_width * usage_factor)
        
        # Add some random noise (±10% of the base value)
        noise = random.uniform(-0.1 * base_value, 0.1 * base_value)
        
        # Calculate final usage
        usage = base_value + noise
        
        return round(min(max(usage, self.min_value), self.max_value), 3)
