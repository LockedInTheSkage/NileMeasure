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

	// Create consumer
	consumer := NewDataConsumer(config)

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
