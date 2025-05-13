package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/nats-io/nats.go"
)

// SensorData represents the structure of incoming sensor data
type SensorData struct {
	SensorType string    `json:"sensorType"`
	SensorID   string    `json:"sensorId"`
	Location   string    `json:"location"`
	Value      float64   `json:"value"`
	Timestamp  time.Time `json:"timestamp"`
}

// DataConsumer handles consuming data from NATS and storing it in InfluxDB
type DataConsumer struct {
	// InfluxDB configuration
	influxURL    string
	influxToken  string
	influxOrg    string
	influxBucket string

	// NATS configuration
	natsURL string

	// Clients
	influxClient influxdb2.Client
	writeAPI     api.WriteAPI
	natsConn     *nats.Conn

	// For graceful shutdown
	ctx        context.Context
	cancelFunc context.CancelFunc
}

// NewDataConsumer creates a new instance of DataConsumer
func NewDataConsumer() *DataConsumer {
	ctx, cancel := context.WithCancel(context.Background())

	return &DataConsumer{
		influxURL:    getEnv("INFLUXDB_URL", "http://influxdb:8086"),
		influxToken:  getEnv("INFLUXDB_TOKEN", ""),
		influxOrg:    getEnv("INFLUXDB_ORG", "acme_corp"),
		influxBucket: getEnv("INFLUXDB_BUCKET", "the_bucket"),
		natsURL:      getEnv("NATS_URL", "nats://nats:4222"),
		ctx:          ctx,
		cancelFunc:   cancel,
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
	
	log.Println("Consumer setup complete")
	return nil
}

// StoreData stores sensor data in InfluxDB
func (c *DataConsumer) StoreData(data SensorData) {
	// Create a point with the sensor data
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

func main() {
	// Setup signal handling for graceful shutdown
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)
	
	consumer := NewDataConsumer()
	
	// Run consumer in a goroutine
	go func() {
		if err := consumer.Run(); err != nil {
			log.Printf("Error in consumer service: %v", err)
		}
	}()
	
	// Wait for termination signal
	<-signals
	log.Println("Received termination signal")
	
	// Cancel the context to initiate shutdown
	consumer.cancelFunc()
	
	// Perform cleanup
	consumer.Shutdown()
}
