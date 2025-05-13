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
	InfluxBucket string

	// NATS configuration
	NatsURL string
}

// NewConfig creates a new Config instance with values from environment variables
func NewConfig() *Config {
	return &Config{
		InfluxURL:    getEnv("INFLUXDB_URL", "http://influxdb:8086"),
		InfluxToken:  getEnv("INFLUXDB_TOKEN", ""),
		InfluxOrg:    getEnv("INFLUXDB_ORG", "acme_corp"),
		InfluxBucket: getEnv("INFLUXDB_BUCKET", "the_bucket"),
		NatsURL:      getEnv("NATS_URL", "nats://nats:4222"),
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
