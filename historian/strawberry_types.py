import strawberry
from typing import Optional

@strawberry.type
class SensorReading:
    sensorId: str
    sensorType: str
    location: str
    value: float
    unit: str
    timestamp: str

@strawberry.type
class AggregatedReading:
    sensorId: str
    sensorType: str
    location: str
    mean: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    sum: Optional[float] = None
    count: Optional[float] = None
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
