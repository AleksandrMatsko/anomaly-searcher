package main

import (
	"context"
	"dummy-observable-app/internal/config"
	"dummy-observable-app/internal/loop"
	metrichole "dummy-observable-app/internal/metric_hole"
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"sync"

	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var cfgPath = flag.String("config", "", "path to config file")

func main() {
	flag.Parse()

	if err := startApp(); err != nil {
		slog.Error("failed to run app", slog.String("error", err.Error()))
		os.Exit(1)
	}
}

func startApp() error {
	if cfgPath == nil || *cfgPath == "" {
		return fmt.Errorf("path to config must be provided")
	}

	cfg, err := config.Read(*cfgPath)
	if err != nil {
		return err
	}

	ctx, cancel := context.WithCancel(context.Background())

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)

	srvMux := http.ServeMux{}
	srvMux.Handle("/metrics", promhttp.Handler())
	srv := http.Server{
		Addr:    fmt.Sprintf("0.0.0.0:%d", cfg.Metrics.Port),
		Handler: &srvMux,
	}

	l := loop.NewLoop(
		metrichole.NewMetricHoleWorker(cfg.MetricHoleWorker),
	)

	wg := sync.WaitGroup{}

	wg.Go(func() {
		<-sigChan
		slog.Info("signal received, shutting down ...")
		cancel()
		srv.Shutdown(context.Background())
	})

	wg.Go(func() {
		slog.Info("listen on", slog.String("addr", srv.Addr))
		if err := srv.ListenAndServe(); err != nil {
			if !errors.Is(err, http.ErrServerClosed) {
				slog.Error("failed to listen and serve", slog.String("error", err.Error()))
			}
		}
	})

	wg.Go(func() {
		slog.Info("start workers")
		l.Start(ctx)
	})
	wg.Wait()

	return nil
}
