package main

import (
	"time"
)

// SensorData represents the structure of incoming sensor data
type SensorData struct {
	SensorType string    `json:"sensorType"`
	SensorID   string    `json:"sensorId"`
	Location   string    `json:"location"`
	Value      float64   `json:"value"`
	Timestamp  time.Time `json:"timestamp"`
}
