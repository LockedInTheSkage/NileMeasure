package main

import (
	"os"
	"strconv"
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
	
	// Alert configuration
	TempAlertThreshold float64
	AlertStateFile     string
}

// NewConfig creates a new Config instance with values from environment variables
func NewConfig() *Config {
	return &Config{
		InfluxURL:          getEnv("INFLUXDB_URL", "http://influxdb:8086"),
		InfluxToken:        getEnv("INFLUXDB_TOKEN", ""),
		InfluxOrg:          getEnv("INFLUXDB_ORG", "acme_corp"),
		InfluxBucket:       getEnv("INFLUXDB_BUCKET", "the_bucket"),
		NatsURL:            getEnv("NATS_URL", "nats://nats:4222"),
		TempAlertThreshold: getEnvFloat("TEMP_ALERT_THRESHOLD", 30.0),
		AlertStateFile:     getEnv("ALERT_STATE_FILE", "/app/data/alert_state.json"),
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

// getEnvFloat gets an environment variable as a float64 or returns a default value
func getEnvFloat(key string, defaultValue float64) float64 {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	
	floatValue, err := strconv.ParseFloat(value, 64)
	if err != nil {
		return defaultValue
	}
	return floatValue
}
