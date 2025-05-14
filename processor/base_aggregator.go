package main

import (
	"context"
)

// BaseAggregator defines the interface for all sensor aggregators
type BaseAggregator interface {
	Setup() error
	Run() error
	Shutdown()
	RunAggregation()
	GetCancelFunc() context.CancelFunc
}

// AggregatorFactory creates appropriate aggregators
type AggregatorFactory struct{}

// CreateAggregators creates all the required aggregators
func (f *AggregatorFactory) CreateAggregators(config *Config) []BaseAggregator {
	return []BaseAggregator{
		NewTemperatureAggregator(config),
		NewHumidityAggregator(config),
		NewElectricityAggregator(config),
	}
}
