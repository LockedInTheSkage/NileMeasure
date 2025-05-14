import strawberry

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
