package metrichole

import (
	"context"
	"dummy-observable-app/internal/config"
	"dummy-observable-app/internal/constants"
	"log/slog"
	"math/rand"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	metricWithHoles = promauto.NewGaugeVec(prometheus.GaugeOpts{
		Namespace: constants.MetricNamespace,
		Name:      "metric_with_holes",
	}, []string{})
)

type metricHoleWorker struct {
	timeout   time.Duration
	normalLen int
	holeLen   int
	state     int
}

func NewMetricHoleWorker(cfg config.MetricHoleWorker) *metricHoleWorker {
	return &metricHoleWorker{
		timeout:   cfg.Timeout,
		normalLen: cfg.NormalLength,
		holeLen:   cfg.HoleLength,
	}
}

func (w *metricHoleWorker) Name() string {
	return "metric_holes_worker"
}

func (w *metricHoleWorker) Timeout() time.Duration {
	return w.timeout
}

func (w *metricHoleWorker) Work(ctx context.Context, _ *slog.Logger) {
	if w.state < w.normalLen {
		metricWithHoles.WithLabelValues().Set(rand.Float64()*2 + 49)
		w.state += 1
		return
	}

	if w.state < w.normalLen+w.holeLen {
		w.state += 1
		return
	}

	w.state = 0
}
