# Sensor Data Simulation System

This project implements a complete sensor data simulation system using Docker containers, including:

1. Sensor simulators (temperature, humidity, electricity) that generate realistic data
2. A message broker (NATS) for pub/sub communication
3. A consumer that stores data in InfluxDB time-series database
4. A GraphQL API with a web-based UI for visualizing the data

## System Architecture

![System Architecture](https://mermaid.ink/img/pako:eNqVkk9PwzAMxb-K5QsIVSs7IJRDJw47IA5oQquxCjRJlbhIaLvvTtqxrYWh7ZT4-fn9nNi5Yb1nJbM-wr5Hnfq3DdiO1A8HwXRjt4HfhbgKZbGxHVo_q0XSSRV8hLqA4nV9XzeQ68k6Y8cUwESj_UFMt6Q92MAvC-NLR4W-UtDV0JBLuq3EBHGPJDrQYw_fxA6LbwhpHNEjPYRgLM3JXDPtDvCEhm4a0qQXxFJnPjzadWQSKzDOOHlBiVnZooLb2IHF5WE-EzIHlbgQlkblDUkBT6gJVAQjkTaoDJoqEZSc9JxPiCbwUvWnb7JDK1S7P3pnWFlk_kpGjCcijWOlppHqiqxF0DwQNDiPyDu0fENh4F0n2B_3JiucfG7VPkucfz5kGKcXeq3AHWmW6eDJUuYfZ3D-D3mJIQbhQ8pcQa5B_xQ2TQwl2-T6_GqI6mLTXGTfWOGhZA?type=png)

## Services

### Sensors
- Simulates various types of sensors (temperature, humidity, electricity usage)
- Generates realistic data with natural variations and patterns
- Publishes data to NATS message broker

### Consumer
- Subscribes to sensor data from NATS
- Processes and stores data in InfluxDB
- Handles error recovery and connection management

### GraphQL API
- Provides a GraphQL interface to query sensor data
- Includes filtering by sensor type, location, and time range
- Offers a web-based dashboard for data visualization

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git (to clone the repository)

### Running the System

1. Clone the repository
2. Run the start script:
   ```
   ./start.sh
   ```
3. Access the web interface at http://localhost:8000

## Web Dashboard

The web dashboard allows you to:
- View real-time sensor data visualizations
- Filter data by sensor type, location, and time range
- Explore individual sensor readings in detail

## Development

### Project Structure
```
├── 2025-05-12-junior-backend-cloud-docker-compose.yaml  # Main docker-compose file
├── start.sh                                            # Startup script
├── sensors/                                            # Sensor simulation service
│   ├── Dockerfile
│   ├── base_sensor.py                                 # Base sensor class
│   ├── temperature_sensor.py                          # Temperature sensor implementation
│   ├── humidity_sensor.py                             # Humidity sensor implementation
│   ├── electricity_sensor.py                          # Electricity usage sensor implementation
│   ├── main.py                                        # Main sensor application
│   └── requirements.txt                               # Python dependencies
├── consumer/                                           # Data consumer service
│   ├── Dockerfile
│   ├── consumer.py                                    # Consumer implementation
│   └── requirements.txt                               # Python dependencies
└── graphql/                                            # GraphQL API service
    ├── Dockerfile
    ├── app.py                                         # GraphQL schema and resolvers
    ├── main.py                                        # FastAPI application
    ├── requirements.txt                               # Python dependencies
    ├── templates/                                     # HTML templates
    │   └── index.html                                # Dashboard template
    └── static/                                        # Static assets
        ├── styles.css                                # CSS styles
        └── app.js                                    # JavaScript for dashboard
```

## Technologies Used

- **Python**: Primary programming language
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

## License

This project is licensed under the MIT License
