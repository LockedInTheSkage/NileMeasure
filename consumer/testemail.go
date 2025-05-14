package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"
)

// sendTestAlert sends a test alert email via NATS
func (c *DataConsumer) sendTestAlert(data SensorData) error {
	// Create test alert message
	alertMsg := map[string]string{
		"subject": "[TEST] Temperature Alert System Check",
		"message": fmt.Sprintf(
			"This is a test email to verify the temperature alert system is working correctly.\n\n"+
				"Test Details:\n"+
				"Sensor ID: %s\n"+
				"Location: %s\n"+
				"Temperature: %.2f°C\n"+
				"Time: %s\n\n"+
				"If you are receiving this email, the alert system is properly configured.",
			data.SensorID,
			data.Location,
			data.Value,
			data.Timestamp.Format(time.RFC1123),
		),
	}

	// Convert to JSON
	jsonData, err := json.Marshal(alertMsg)
	if err != nil {
		log.Printf("Failed to create test alert message: %v", err)
		return err
	}

	// Send to email service via NATS
	err = c.natsConn.Publish("emails", jsonData)
	if err != nil {
		log.Printf("Failed to send test alert via NATS: %v", err)
		return err
	}

	log.Printf("Test alert sent successfully")
	return nil
}
