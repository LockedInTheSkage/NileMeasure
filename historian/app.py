import os
from datetime import datetime, timedelta
from typing import List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from influxdb_client import InfluxDBClient
from strawberry_types import SensorReading, LocationInfo, SensorInfo, AggregatedReading



# InfluxDB configuration
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "acme_corp")
INFLUXDB_RAW_BUCKET = os.environ.get("INFLUXDB_RAW_BUCKET", "sensor_data")
INFLUXDB_AGGREGATED_BUCKET = os.environ.get("INFLUXDB_AGGREGATED_BUCKET", "aggregated_data")

# Initialize InfluxDB client
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
query_api = influx_client.query_api()



def get_all_locations() -> List[LocationInfo]:
    """Get all locations with sensor counts."""
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.measurements(bucket: "{INFLUXDB_RAW_BUCKET}")
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
    from(bucket: "{INFLUXDB_RAW_BUCKET}")
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
        startTime = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
    if not endTime:
        endTime = datetime.now().isoformat() + "Z"
    
    # Build the Flux query
    query = f'''
    from(bucket: "{INFLUXDB_RAW_BUCKET}")
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

def get_aggregated_readings(
    sensorType: Optional[str] = None,
    sensorId: Optional[str] = None,
    location: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    limit: int = 100
) -> List[AggregatedReading]:
    """Query aggregated sensor readings from InfluxDB with filters."""
    # Set default time range if not provided
    if not startTime:
        startTime = (datetime.now() - timedelta(hours=24)).isoformat() + "Z"
    if not endTime:
        endTime = datetime.now().isoformat() + "Z"
    
    # Determine which aggregated measurements to query based on sensorType
    measurements = []
    if sensorType:
        measurements = [f"{sensorType}_aggregated"]
    else:
        measurements = ["temperature_aggregated", "humidity_aggregated", "electricity_aggregated"]
    
    aggregated_readings = []
    
    for measurement in measurements:
        # Extract the base sensor type from the measurement name
        base_sensor_type = measurement.replace("_aggregated", "")
        
        # Build the Flux query
        query = f'''
        from(bucket: "{INFLUXDB_AGGREGATED_BUCKET}")
            |> range(start: {startTime}, stop: {endTime})
            |> filter(fn: (r) => r._measurement == "{measurement}")
        '''
        
        if sensorId:
            query += f'|> filter(fn: (r) => r.sensorId == "{sensorId}")\n'
        
        if location:
            query += f'|> filter(fn: (r) => r.location == "{location}")\n'
        
        # Group by sensorId, location, and time to get the most recent readings
        query += '''
            |> pivot(rowKey:["_time"], columnKey: ["type"], valueColumn: "_value")
            |> group(columns: ["sensorId", "location"])
            |> sort(columns: ["_time"], desc: true)
        '''
        
        if limit > 0:
            query += f'|> limit(n: {limit})\n'
        
        try:
            # Execute the query
            tables = query_api.query(query)
            
            # Parse the results
            for table in tables:
                for record in table.records:
                    # Check if all aggregation values are present
                    mean_value = record.values.get("mean", 0.0)
                    min_value = record.values.get("min", 0.0)
                    max_value = record.values.get("max", 0.0)
                    count_value = record.values.get("count", 0.0)
                    sum_value = record.values.get("sum", 0.0)
                    
                    reading = AggregatedReading(
                        sensorId=record.values.get("sensorId", ""),
                        sensorType=base_sensor_type,
                        location=record.values.get("location", ""),
                        mean=mean_value,
                        min=min_value,
                        max=max_value,
                        count=count_value,
                        sum=sum_value,
                        unit=get_unit_by_sensorType(base_sensor_type),
                        timestamp=record.values.get("_time").isoformat()
                    )
                    aggregated_readings.append(reading)
        except Exception as e:
            print(f"Error querying InfluxDB for aggregated data: {e}")
    
    return aggregated_readings

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
    
    @strawberry.field
    def aggregatedReadings(
        self, 
        sensorType: Optional[str] = None,
        sensorId: Optional[str] = None,
        location: Optional[str] = None,
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
        limit: int = 100
    ) -> List[AggregatedReading]:
        return get_aggregated_readings(
            sensorType=sensorType,
            sensorId=sensorId,
            location=location,
            startTime=startTime,
            endTime=endTime,
            limit=limit
        )



# Create GraphQL schema
schema = strawberry.Schema(query=Query)

# Create FastAPI app with GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
