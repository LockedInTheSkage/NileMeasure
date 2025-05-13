# Junior Backend Cloud Developer Technical Challenge

## OVERVIEW

Design and implement a distributed, event-driven system for building automation data processing. Your solution should consist of multiple microservices that communicate through NATS messaging system and store time-series data in InfluxDB v2.

This challenge is intentionally larger than what can be realistically completed in 9 hours. You are expected to decide which components to implement fully and which to address conceptually.

We have provided a scaffold docker-compose.yml file that includes pre-configured NATS and InfluxDB v2 services. You should extend this file with your own services.

## CORE REQUIREMENTS

1. Multiple Services:
   - Data Ingestion Service: Simulates building sensors by generating realistic time-series data (temperature, humidity, energy usage, etc.) and publishes simulated data to NATS for consumption by other services
   - Processing Service: Stores the incoming data in raw and aggregated form (meaningful aggregations for IoT data) to InfluxDB
   - Historian Service: Exposes raw and aggregated time series data from InfluxDB via GraphQL
   - Alerting Service: Monitors thresholds and generates notifications

2. Event-Driven Communication:
   - Use the provided NATS service for inter-service communication
   - Implement appropriate subjects/topics for different event types
   - Handle error cases and ensure message delivery

3. Data Storage:
   - Use the provided InfluxDB v2 for storing time-series data
   - Design appropriate bucket(s) and measurement structure
   - Implement queries that leverage InfluxDB's time-series capabilities

4. GraphQL API:
   - Design a GraphQL schema appropriate for building automation data
   - Implement queries to retrieve sensor data with flexible filtering
   - Support aggregations and data transformations through GraphQL resolvers

## TECHNICAL CONSTRAINTS

- Use Python and/or Go for service implementation
- Your services should be containerized and added to the provided docker-compose.yml
- Include proper environment configuration and documentation
    