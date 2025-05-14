# Sensor Data Simulation System

This projec### Running the System

1. Clone the repository
2. (Optional) Create a `.env` file with your database credentials or let the start script create one for you
3. Run the start script:
   ```
   ./start.sh
   ```
4. Access the web interface at http://localhost:8000

### Environment Configuration

The system uses an `.env` file to store sensitive configuration values. If this file doesn't exist when you run `start.sh`, a sample file with random credentials will be created automatically.

You can customize the following variables in the `.env` file:

```
# InfluxDB Configuration
INFLUXDB_ADMIN_USERNAME=admin
INFLUXDB_ADMIN_PASSWORD=YourSecurePassword
INFLUXDB_ORG=acme_corp
INFLUXDB_BUCKET=sensor_data
INFLUXDB_AGGREGATED_BUCKET=aggregated_data
INFLUXDB_ADMIN_TOKEN=YourInfluxDBToken

# Alert Configuration
TEMP_ALERT_THRESHOLD=30.0
```

## Security

### Credential Management

The system uses environment variables for sensitive configuration, following best practices:

1. Database credentials and tokens are stored in a `.env` file that is not committed to version control
2. Email credentials are stored in a separate configuration file (`alert/config/email_config.json`)
3. Sample configuration files are provided as templates (`.env.sample` and `email_config.sample.json`)

### Generating New Credentials

To generate new credentials for InfluxDB:

```bash
# Generate a new random password (16 characters, hexadecimal)
openssl rand -hex 16

# Generate a new random token (64 characters, base64-encoded)
openssl rand -base64 64
```

For Gmail accounts used in email alerts, generate an App Password:
1. Go to your Google Account > Security > 2-Step Verification
2. At the bottom, select "App passwords"
3. Create a new app password for this application
4. Use this password in the `email_config.json` fileents a complete sensor data simulation system using Docker containers, including:

1. Sensor simulators (temperature, humidity, electricity) that generate realistic data
2. A message broker (NATS) for pub/sub communication
3. A consumer that stores data in InfluxDB time-series database
4. A data processor that aggregates sensor readings
5. An email alert service that sends notifications based on predefined triggers
6. A GraphQL API with a web-based UI for visualizing the data

## Services

### Sensors
- Simulates various types of sensors (temperature, humidity, electricity usage)
- Generates realistic data with natural variations and patterns
- Publishes data to NATS message broker

### Consumer
- Subscribes to sensor data from NATS
- Processes and stores data in InfluxDB
- Sends alert messages when sensor values exceed thresholds

### Processor
- Aggregates sensor data over time periods
- Calculates statistics (min, max, mean, sum, count)
- Stores aggregated data for efficient querying

### Alert Service
- Listens for alert messages on NATS
- Sends email notifications for critical conditions
- Uses configurable email settings. Check `Email Alerts Configuration` for details

### GraphQL API
- Provides a GraphQL interface to query sensor data
- Includes filtering by sensor type, location, and time range
- Supports querying both raw and aggregated data

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git (to clone the repository)

### Running the System

1. Clone the repository
2. Enter environment variables in the `.env` file
3. Run the start script:
   ```
   ./start.sh
   ```
4. Access the graphQL interface at http://localhost:8000/graphql


## GraphQL API Usage

The system provides a GraphQL API with the following query types:

### sensorReadings
Retrieves raw sensor readings with optional filtering.

Example query:
```graphql
query {
  sensorReadings(
    sensorType: "temperature", 
    location: "living_room", 
    startTime: "2025-05-13T00:00:00Z", 
    endTime: "2025-05-14T00:00:00Z", 
    limit: 10
  ) {
    sensorId
    sensorType
    location
    value
    unit
    timestamp
  }
}
```

### aggregatedReadings
Retrieves aggregated sensor data (min, max, mean, etc.).

Example query:
```graphql
query {
  aggregatedReadings(
    sensorType: "humidity", 
    location: "kitchen", 
    limit: 5
  ) {
    sensorId
    sensorType
    location
    min
    max
    mean
    count
    sum
    unit
    timestamp
  }
}
```

### sensors
Lists all available sensors in the system.

Example query:
```graphql
query {
  sensors {
    sensorId
    sensorType
    location
  }
}
```

### locations
Lists all locations with sensor counts.

Example query:
```graphql
query {
  locations {
    name
    sensorCount
  }
}
```

## Email Alerts Configuration

The system can send email alerts when sensor readings exceed predefined thresholds. To configure the email settings, modify the file at:

```
alert/config/email_config.json
```

The configuration requires the following fields:
- `from_email`: The sender email address (Gmail account)
- `from_password`: App password for Gmail (not your regular account password)
- `to_email`: The recipient email address

Example configuration:
```json
{
  "from_email": "your.email@gmail.com",
  "from_password": "your-app-password",
  "to_email": "recipient@example.com"
}
```

## Development
### Project Structure
```
├── 2025-05-12-junior-backend-cloud-docker-compose.yaml
├── start.sh
├── sensors/
│   ├── Dockerfile  
│   ├── base_sensor.py
│   ├── temperature_sensor.py
│   ├── humidity_sensor.py
│   ├── electricity_sensor.py
│   ├── main.py
│   └── requirements.txt
├── consumer/
│   ├── Dockerfile
│   ├── main.go
│   ├── dataconsumer.go
│   ├── sensordata.go
│   ├── alert.go
│   ├── config.go
│   ├── go.mod
│   └── go.sum
├── processor/
│   ├── Dockerfile
│   ├── main.go
│   ├── base_aggregator.go
│   ├── temperature_aggregator.go
│   ├── humidity_aggregator.go
│   ├── electricity_aggregator.go
│   ├── config.go
│   ├── go.mod
│   └── go.sum
├── alert/
│   ├── Dockerfile
│   ├── main.py
│   ├── config/
│   │   ├── email_config.json
│   │   └── README.md
└── historian/
    ├── Dockerfile
    ├── app.py
    ├── main.py
    ├── strawberry_types.py
    ├── requirements.txt
    ├── templates/
    │   └── index.html
    └── static/
        ├── styles.css
        └── app.js
```

## Technologies Used

- **Python**: Primary programming language for sensors, API, and alert services
- **Go**: Used for consumer and data processor services
- **NATS**: Message broker for pub/sub
- **InfluxDB**: Time-series database
- **FastAPI**: Web framework
- **Strawberry**: GraphQL library
- **Chart.js**: JavaScript charting library
- **Docker**: Containerization

## Adding New Sensor Types

To add a new sensor type:

1. Create a new sensor class in the `sensors` directory
2. Inherit from `BaseSensor` class
3. Implement the `generate_reading` method
4. Add instances of your new sensor in `main.py`
5. Create a corresponding aggregator in the `processor` directory
6. Update the consumer to handle the new sensor type

## Configuring Alert Thresholds

Alert thresholds are defined in the consumer service. To modify the thresholds:

1. Navigate to the `consumer/alert.go` file
2. Update the threshold values for existing sensor types
3. Add new threshold configurations for any new sensor types

## License

This project is licensed under the MIT License
