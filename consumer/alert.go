package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

// AlertState stores information about the last alert sent
type AlertState struct {
	LastAlertTime time.Time `json:"lastAlertTime"`
}

// shouldSendAlert checks if we should send an alert based on the last alert time
func (c *DataConsumer) shouldSendAlert() bool {
	// Create directory for alert state file if it doesn't exist
	dir := filepath.Dir(c.alertStateFile)
	if err := os.MkdirAll(dir, 0755); err != nil {
		log.Printf("Failed to create directory for alert state file: %v", err)
		return true // Send alert if we can't check the state
	}

	// Check if alert state file exists
	state, err := c.loadAlertState()
	if err != nil {
		log.Printf("Failed to load alert state: %v", err)
		return true // Send alert if we can't load previous state
	}

	// Check if 24 hours have passed since the last alert
	now := time.Now()
	if now.Sub(state.LastAlertTime) < 24*time.Hour {
		log.Printf("Alert already sent today at %v, not sending again", state.LastAlertTime)
		return false
	}

	return true
}

// loadAlertState loads the alert state from the file
func (c *DataConsumer) loadAlertState() (AlertState, error) {
	var state AlertState

	// Check if file exists
	if _, err := os.Stat(c.alertStateFile); os.IsNotExist(err) {
		// Return empty state if file doesn't exist
		return state, nil
	}

	// Read file
	data, err := os.ReadFile(c.alertStateFile)
	if err != nil {
		return state, err
	}

	// Parse JSON
	if len(data) > 0 {
		err = json.Unmarshal(data, &state)
		if err != nil {
			return state, err
		}
	}

	return state, nil
}

// saveAlertState saves the current alert state to the file
func (c *DataConsumer) saveAlertState(state AlertState) error {
	// Marshal to JSON
	data, err := json.Marshal(state)
	if err != nil {
		return err
	}

	// Write to file
	return os.WriteFile(c.alertStateFile, data, 0644)
}

// sendTemperatureAlert sends a temperature alert via NATS to the email service
func (c *DataConsumer) sendTemperatureAlert(data SensorData) error {
	// Create alert message
	alertMsg := map[string]string{
		"subject": fmt.Sprintf("High Temperature Alert: %.2f°C", data.Value),
		"message": fmt.Sprintf(
			"Warning: High temperature detected!\n\n"+
				"Sensor ID: %s\n"+
				"Location: %s\n"+
				"Temperature: %.2f°C\n"+
				"Time: %s\n\n"+
				"Please check the system as soon as possible.",
			data.SensorID,
			data.Location,
			data.Value,
			data.Timestamp.Format(time.RFC1123),
		),
	}

	// Convert to JSON
	jsonData, err := json.Marshal(alertMsg)
	if err != nil {
		log.Printf("Failed to create alert message: %v", err)
		return err
	}

	// Send to email service via NATS
	err = c.natsConn.Publish("emails", jsonData)
	if err != nil {
		log.Printf("Failed to send alert via NATS: %v", err)
		return err
	}

	log.Printf("Temperature alert sent for sensor %s", data.SensorID)

	// Update alert state
	now := time.Now()
	state := AlertState{LastAlertTime: now}
	if err := c.saveAlertState(state); err != nil {
		log.Printf("Failed to save alert state: %v", err)
	}

	return nil
}
