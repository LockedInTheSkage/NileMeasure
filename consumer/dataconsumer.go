package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/nats-io/nats.go"
)

// DataConsumer handles consuming data from NATS and storing it in InfluxDB
type DataConsumer struct { // something
	// InfluxDB configuration
	influxURL    string
	influxToken  string
	influxOrg    string
	influxBucket string

	// NATS configuration
	natsURL string

	// Alert configuration
	tempAlertThreshold float64
	alertStateFile     string

	// Clients
	influxClient influxdb2.Client
	writeAPI     api.WriteAPI
	natsConn     *nats.Conn

	// For graceful shutdown
	ctx        context.Context
	cancelFunc context.CancelFunc
}

// NewDataConsumer creates a new instance of DataConsumer
func NewDataConsumer(config *Config) *DataConsumer {
	ctx, cancel := context.WithCancel(context.Background())

	return &DataConsumer{
		influxURL:          config.InfluxURL,
		influxToken:        config.InfluxToken,
		influxOrg:          config.InfluxOrg,
		influxBucket:       config.InfluxBucket,
		natsURL:            config.NatsURL,
		tempAlertThreshold: config.TempAlertThreshold,
		alertStateFile:     config.AlertStateFile,
		ctx:                ctx,
		cancelFunc:         cancel,
	}
}

// Setup initializes connections to InfluxDB and NATS
func (c *DataConsumer) Setup() error {
	// Connect to InfluxDB
	log.Printf("Connecting to InfluxDB at %s", c.influxURL)
	log.Printf("InfluxDB token: %s", c.influxToken)

	c.influxClient = influxdb2.NewClient(c.influxURL, c.influxToken)
	c.writeAPI = c.influxClient.WriteAPI(c.influxOrg, c.influxBucket)

	// Setup error handling for InfluxDB write errors
	errorsCh := c.writeAPI.Errors()
	go func() {
		for err := range errorsCh {
			log.Printf("InfluxDB write error: %s", err.Error())
		}
	}()

	// Connect to NATS
	log.Printf("Connecting to NATS at %s", c.natsURL)
	var err error
	c.natsConn, err = nats.Connect(c.natsURL)
	if err != nil {
		return fmt.Errorf("failed to connect to NATS: %w", err)
	}
	
	// Ensure alert state directory exists
	alertDir := filepath.Dir(c.alertStateFile)
	if err := os.MkdirAll(alertDir, 0755); err != nil {
		log.Printf("Warning: Failed to create alert state directory: %v", err)
	}

	// Send a test email to verify the alert system
	go func() {
		// Wait a bit for all services to start up
		time.Sleep(5 * time.Second)
		
		testData := SensorData{
			SensorType: "temperature",
			SensorID:   "test_sensor",
			Location:   "Test Location",
			Value:      35.0, // Above the threshold to trigger an alert
			Timestamp:  time.Now(),
		}
		
		log.Println("Sending test temperature alert email...")
		if err := c.sendTestAlert(testData); err != nil {
			log.Printf("Failed to send test alert: %v", err)
		} else {
			log.Println("Test alert sent successfully!")
		}
	}()

	log.Println("Consumer setup complete")
	return nil
}

// StoreData stores sensor data in InfluxDB
func (c *DataConsumer) StoreData(data SensorData) {
	
	p := influxdb2.NewPointWithMeasurement(data.SensorType).
		AddTag("sensorId", data.SensorID).
		AddTag("location", data.Location).
		AddField("value", data.Value).
		SetTime(data.Timestamp)

	// Write to InfluxDB
	c.writeAPI.WritePoint(p)
	log.Printf("Stored data for %s sensor %s", data.SensorType, data.SensorID)
}

// MessageHandler handles incoming NATS messages
func (c *DataConsumer) MessageHandler(msg *nats.Msg) {
	// Decode and parse the message
	var data SensorData
	err := json.Unmarshal(msg.Data, &data)
	if err != nil {
		log.Printf("Failed to decode message: %v", err)
		return
	}

	log.Printf("Received message: %+v", data)

	// Store the data in InfluxDB
	c.StoreData(data)
	
	// Check for temperature alerts
	if data.SensorType == "temperature" && data.Value > c.tempAlertThreshold {
		log.Printf("High temperature detected: %.2f°C at %s", data.Value, data.Location)
		if c.shouldSendAlert() {
			c.sendTemperatureAlert(data)
		}
	}
}

// SubscribeToSensors subscribes to all sensor topics
func (c *DataConsumer) SubscribeToSensors() error {
	// Subscribe to all sensor data
	_, err := c.natsConn.Subscribe("sensors.>", c.MessageHandler)
	if err != nil {
		return fmt.Errorf("error subscribing to topics: %w", err)
	}

	log.Println("Subscribed to all sensor topics")
	return nil
}

// Run starts the consumer service
func (c *DataConsumer) Run() error {
	// Setup connections
	if err := c.Setup(); err != nil {
		return err
	}

	// Subscribe to sensor topics
	if err := c.SubscribeToSensors(); err != nil {
		return err
	}

	// Wait for termination signal
	<-c.ctx.Done()
	return nil
}

// Shutdown performs a graceful shutdown
func (c *DataConsumer) Shutdown() {
	log.Println("Shutting down consumer service...")

	// Flush any buffered points
	if c.writeAPI != nil {
		c.writeAPI.Flush()
	}

	// Close clients
	if c.influxClient != nil {
		c.influxClient.Close()
	}

	if c.natsConn != nil {
		c.natsConn.Close()
	}

	log.Println("Consumer service shutdown complete")
}
