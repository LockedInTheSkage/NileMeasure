import asyncio
import os
import nats
import logging
from temperature_sensor import TemperatureSensor
from humidity_sensor import HumiditySensor
from electricity_sensor import ElectricityUsageSensor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("main")

async def setup_sensors():
    # Connect to NATS
    nats_url = os.environ.get("NATS_URL", "nats://nats:4222")
    logger.info(f"Connecting to NATS at {nats_url}")
    nc = await nats.connect(nats_url)
    
    # Create sensors
    sensors = [
        # Temperature sensors
        TemperatureSensor(sensorId="temp_001", location="Living Room", min_value=18.0, max_value=26.0, interval=5),
        TemperatureSensor(sensorId="temp_002", location="Kitchen", min_value=19.0, max_value=28.0, interval=5),
        TemperatureSensor(sensorId="temp_003", location="Bedroom", min_value=16.0, max_value=24.0, interval=5),
        TemperatureSensor(sensorId="temp_004", location="Outside", min_value=5.0, max_value=35.0, interval=5),
        
        # Humidity sensors
        HumiditySensor(sensorId="hum_001", location="Living Room", min_value=40.0, max_value=60.0, interval=7),
        HumiditySensor(sensorId="hum_002", location="Kitchen", min_value=45.0, max_value=70.0, interval=7),
        HumiditySensor(sensorId="hum_003", location="Bathroom", min_value=50.0, max_value=85.0, interval=7),
        
        # Electricity usage sensors
        ElectricityUsageSensor(sensorId="elec_001", location="Main Panel", min_value=0.5, max_value=8.0, interval=10),
        ElectricityUsageSensor(sensorId="elec_002", location="Kitchen", min_value=0.1, max_value=3.0, interval=10),
        ElectricityUsageSensor(sensorId="elec_003", location="Living Room", min_value=0.05, max_value=2.0, interval=10),
    ]
    
    # Create tasks for each sensor
    tasks = [sensor.run(nc) for sensor in sensors]
    
    # Run all sensors concurrently
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error running sensors: {e}")
    finally:
        await nc.close()

if __name__ == "__main__":
    try:
        asyncio.run(setup_sensors())
    except KeyboardInterrupt:
        logger.info("Sensor simulation stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
