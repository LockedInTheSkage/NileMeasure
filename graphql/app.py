import os
from datetime import datetime, timedelta
from typing import List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from influxdb_client import InfluxDBClient
from pydantic import BaseModel

# InfluxDB configuration
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "acme_corp")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "the_bucket")

# Initialize InfluxDB client
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
query_api = influx_client.query_api()

# Define GraphQL types
@strawberry.type
class SensorReading:
    sensorId: str
    sensorType: str
    location: str
    value: float
    unit: str
    timestamp: str

@strawberry.type
class LocationInfo:
    name: str
    sensorCount: int

@strawberry.type
class SensorInfo:
    sensorId: str
    sensorType: str
    location: str
    
def get_all_locations() -> List[LocationInfo]:
    """Get all locations with sensor counts."""
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.measurements(bucket: "{INFLUXDB_BUCKET}")
        |> schema.tagKeys()
        |> filter(fn: (r) => r._value == "location")
        |> group()
        |> yield()
    '''
    
    try:
        tables = query_api.query(query)
        location_counts = {}
        
        for table in tables:
            for record in table.records:
                location = record.values.get("location")
                if location:
                    location_counts[location] = location_counts.get(location, 0) + 1
        
        return [
            LocationInfo(name=location, sensorCount=count)
            for location, count in location_counts.items()
        ]
    except Exception as e:
        print(f"Error getting locations: {e}")
        return []

def get_all_sensors() -> List[SensorInfo]:
    """Get all sensors."""
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -1h)
        |> group(columns: ["sensorId", "location", "_measurement"])
        |> distinct(column: "sensorId")
        |> yield()
    '''
    
    try:
        tables = query_api.query(query)
        sensors = []
        
        for table in tables:
            for record in table.records:
                sensor = SensorInfo(
                    sensorId=record.values.get("sensorId", ""),
                    sensorType=record.values.get("_measurement", ""),
                    location=record.values.get("location", "")
                )
                sensors.append(sensor)
        
        return sensors
    except Exception as e:
        print(f"Error getting sensors: {e}")
        return []

def get_sensor_readings(
    sensorType: Optional[str] = None,
    sensorId: Optional[str] = None,
    location: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    limit: int = 100
) -> List[SensorReading]:
    """Query sensor readings from InfluxDB with filters."""
    # Set default time range if not provided
    if not startTime:
        startTime = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
    if not endTime:
        endTime = datetime.utcnow().isoformat() + "Z"
    
    # Build the Flux query
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: {startTime}, stop: {endTime})
    '''
    
    # Add filters if provided
    if sensorType:
        query += f'|> filter(fn: (r) => r._measurement == "{sensorType}")\n'
    
    if sensorId:
        query += f'|> filter(fn: (r) => r.sensorId == "{sensorId}")\n'
    
    if location:
        query += f'|> filter(fn: (r) => r.location == "{location}")\n'
    
    # Add sort and limit
    query += f'''
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: {limit})
    '''
    
    try:
        # Execute the query
        tables = query_api.query(query)
        readings = []
        
        # Parse the results
        for table in tables:
            for record in table.records:
                reading = SensorReading(
                    sensorId=record.values.get("sensorId", ""),
                    sensorType=record.values.get("_measurement", ""),
                    location=record.values.get("location", ""),
                    value=record.values.get("_value", 0.0),
                    unit=get_unit_by_sensorType(record.values.get("_measurement", "")),
                    timestamp=record.values.get("_time").isoformat()
                )
                readings.append(reading)
        
        return readings
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return []

def get_unit_by_sensorType(sensorType: str) -> str:
    """Return the appropriate unit for a sensor type."""
    units = {
        "temperature": "°C",
        "humidity": "%",
        "electricity": "kW"
    }
    return units.get(sensorType, "")

# Define GraphQL resolvers
@strawberry.type
class Query:
    @strawberry.field
    def sensorReadings(
        self, 
        sensorType: Optional[str] = None,
        sensorId: Optional[str] = None,
        location: Optional[str] = None,
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
        limit: int = 100
    ) -> List[SensorReading]:
        return get_sensor_readings(
            sensorType=sensorType,
            sensorId=sensorId,
            location=location,
            startTime=startTime,
            endTime=endTime,
            limit=limit
        )
    
    @strawberry.field
    def locations(self) -> List[LocationInfo]:
        return get_all_locations()
    
    @strawberry.field
    def sensors(self) -> List[SensorInfo]:
        return get_all_sensors()

# Create GraphQL schema
schema = strawberry.Schema(query=Query)

# Create FastAPI app with GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
