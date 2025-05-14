package main

import (
	"os"
)

// Config holds the application configuration
type Config struct {
	// InfluxDB configuration
	InfluxURL    string
	InfluxToken  string
	InfluxOrg    string
	SourceBucket string
	TargetBucket string

	// Aggregation configuration
	AggregationInterval string
}

// NewConfig creates a new Config instance with values from environment variables
func NewConfig() *Config {
	return &Config{
		InfluxURL:           getEnv("INFLUXDB_URL", "http://influxdb:8086"),
		InfluxToken:         getEnv("INFLUXDB_TOKEN", ""),
		InfluxOrg:           getEnv("INFLUXDB_ORG", "acme_corp"),
		SourceBucket:        getEnv("INFLUXDB_SOURCE_BUCKET", "sensor_data"),
		TargetBucket:        getEnv("INFLUXDB_TARGET_BUCKET", "aggregated_data"),
		AggregationInterval: getEnv("AGGREGATION_INTERVAL", "30m"),
	}
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
