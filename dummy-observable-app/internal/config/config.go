package config

import (
	"fmt"
	"os"
	"time"

	"go.yaml.in/yaml/v2"
)

type Config struct {
	Metrics          Metrics          `yaml:"metrics"`
	MetricHoleWorker MetricHoleWorker `yaml:"metricHoleWorker"`
}

type Metrics struct {
	Port int `yaml:"port"`
}

type MetricHoleWorker struct {
	Timeout      time.Duration `yaml:"timeout"`
	NormalLength int           `yaml:"normalLength"`
	HoleLength   int           `yaml:"holeLength"`
}

func Read(path string) (Config, error) {
	f, err := os.Open(path)
	if err != nil {
		return Config{}, fmt.Errorf("failed to open file: %w", err)
	}
	defer f.Close()

	decoder := yaml.NewDecoder(f)

	cfg := Config{}
	if err = decoder.Decode(&cfg); err != nil {
		return Config{}, fmt.Errorf("failed to decode config file: %w", err)
	}

	return cfg, nil
}
