package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	// Setup signal handling for graceful shutdown
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)

	// Load configuration
	config := NewConfig()

	// Create aggregators
	factory := &AggregatorFactory{}
	aggregators := factory.CreateAggregators(config)

	// Run aggregators in goroutines
	for _, agg := range aggregators {
		aggregator := agg // Create a local copy for the closure
		go func() {
			if err := aggregator.Run(); err != nil {
				log.Printf("Error in aggregator service: %v", err)
			}
		}()
	}

	// Wait for termination signal
	<-signals
	log.Println("Received termination signal")

	// Cancel the context to initiate shutdown for all aggregators
	for _, aggregator := range aggregators {
		aggregator.GetCancelFunc()()
		aggregator.Shutdown()
	}
}
