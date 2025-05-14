package main

import (
	"context"
	"fmt"
	"log"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
)

// ElectricityAggregator handles aggregating electricity data in InfluxDB
type ElectricityAggregator struct {
	// InfluxDB configuration
	influxURL    string
	influxToken  string
	influxOrg    string
	influxBucket string

	// Aggregation configuration
	aggregationInterval string

	// Clients
	influxClient influxdb2.Client
	queryAPI     api.QueryAPI
	writeAPI     api.WriteAPIBlocking

	// For graceful shutdown
	ctx        context.Context
	cancelFunc context.CancelFunc
}

// NewElectricityAggregator creates a new ElectricityAggregator instance
func NewElectricityAggregator(config *Config) *ElectricityAggregator {
	ctx, cancel := context.WithCancel(context.Background())

	return &ElectricityAggregator{
		influxURL:           config.InfluxURL,
		influxToken:         config.InfluxToken,
		influxOrg:           config.InfluxOrg,
		influxBucket:        config.InfluxBucket,
		aggregationInterval: config.AggregationInterval,
		ctx:                 ctx,
		cancelFunc:          cancel,
	}
}

// GetCancelFunc returns the cancel function for this aggregator
func (a *ElectricityAggregator) GetCancelFunc() context.CancelFunc {
	return a.cancelFunc
}

// Setup initializes connections to InfluxDB
func (a *ElectricityAggregator) Setup() error {
	log.Printf("[Electricity] Connecting to InfluxDB at %s", a.influxURL)
	
	a.influxClient = influxdb2.NewClient(a.influxURL, a.influxToken)
	a.queryAPI = a.influxClient.QueryAPI(a.influxOrg)
	a.writeAPI = a.influxClient.WriteAPIBlocking(a.influxOrg, a.influxBucket)
	
	log.Println("[Electricity] Aggregator setup complete")
	return nil
}

// Run starts the electricity aggregator service
func (a *ElectricityAggregator) Run() error {
	// Setup connections
	if err := a.Setup(); err != nil {
		return err
	}

	// Parse aggregation interval
	interval, err := time.ParseDuration(a.aggregationInterval)
	if err != nil {
		return fmt.Errorf("[Electricity] invalid aggregation interval: %w", err)
	}

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	// Run immediately on startup
	a.RunAggregation()

	// Continue running on the ticker until context is canceled
	for {
		select {
		case <-ticker.C:
			a.RunAggregation()
		case <-a.ctx.Done():
			return nil
		}
	}
}
// RunAggregation performs one electricity aggregation cycle
func (a *ElectricityAggregator) RunAggregation() {
	log.Println("[Electricity] Starting aggregation...")

	sensorType := "electricity"

	aggregationTypes := []string{"mean", "min", "max", "sum", "count"}
	
	// Process each aggregation type
	for _, aggType := range aggregationTypes {
		// Build the Flux query for this aggregation type
		flux := fmt.Sprintf(`
from(bucket: "%s")
  |> range(start: -%s)
  |> filter(fn: (r) => r._measurement == "%s")
  |> group(columns: ["sensorId", "location"])
  |> aggregateWindow(every: %s, fn: %s, createEmpty: false)
  |> yield(name: "%s")
`, a.influxBucket, a.aggregationInterval, sensorType, a.aggregationInterval, aggType, aggType)

		// Execute the query
		result, err := a.queryAPI.Query(context.Background(), flux)
		if err != nil {
			log.Printf("[Electricity] Query error for %s: %v", aggType, err)
			continue
		}

		// Process and store the aggregated results
		for result.Next() {
			record := result.Record()
			
			value := record.Value()


			// Check if the value is a float, if it is interger, convert it to float
			if v, ok := value.(int64); ok {
				value = float64(v)
			} else if v, ok := value.(float64); ok {
				value = v
			} else {
				log.Printf("[Temperature] Unexpected value type: %T", value)
				continue
			}

			
			sensorID := record.ValueByKey("sensorId").(string)
			location := record.ValueByKey("location").(string)
			timestamp := record.Time()
			
			// Create a point with the aggregated value
			point := influxdb2.NewPoint(
				sensorType+"_aggregated",
				map[string]string{
					"sensorId": sensorID,
					"location": location,
					"type":     aggType,
				},
				map[string]interface{}{
					"value": value,
				},
				timestamp,
			)

			err := a.writeAPI.WritePoint(context.Background(), point)
			if err != nil {
				log.Printf("[Electricity] Write error: %v", err)
			} else {
				log.Printf("[Electricity] Wrote aggregated point (%s) for sensor %s at %s: %v", 
					aggType, sensorID, timestamp, value)
			}
		}

		if result.Err() != nil {
			log.Printf("[Electricity] Query parsing error for %s: %v", aggType, result.Err())
		}
	}
}

// Shutdown performs a graceful shutdown
func (a *ElectricityAggregator) Shutdown() {
	log.Println("[Electricity] Shutting down aggregator service...")

	if a.influxClient != nil {
		a.influxClient.Close()
	}

	log.Println("[Electricity] Aggregator service shutdown complete")
}
