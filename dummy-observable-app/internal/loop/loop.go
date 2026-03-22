package loop

import (
	"context"
	"fmt"
	"log/slog"
	"runtime/debug"
	"sync"
	"time"
)

type LoopWorker interface {
	Name() string
	Timeout() time.Duration
	Work(ctx context.Context, logger *slog.Logger)
}

type loop struct {
	workers []LoopWorker
}

func NewLoop(workers ...LoopWorker) *loop {
	return &loop{
		workers: workers,
	}
}

func (l *loop) Start(ctx context.Context) {
	wg := sync.WaitGroup{}

	for _, w := range l.workers {
		wg.Go(func() {
			l.runSingleWorker(ctx, w)
		})
	}

	wg.Wait()
}

func (l *loop) runSingleWorker(ctx context.Context, w LoopWorker) {
	ticker := time.NewTicker(w.Timeout())
	logger := slog.Default().With("worker_name", w.Name())

	logger.Info("run worker")
	for {
		select {
		case <-ctx.Done():
			logger.Info("shutdown")
			return
		case <-ticker.C:
			wrapWithPanicHandler(ctx, logger, w)
		}
	}
}

func wrapWithPanicHandler(ctx context.Context, logger *slog.Logger, w LoopWorker) {
	defer func() {
		if err := recover(); err != nil {
			logger.Error("panic recovered", slog.String("error", fmt.Sprintf("%v", err)))
			logger.Info("stack trace", slog.String("stack", string(debug.Stack())))
		}
	}()

	w.Work(ctx, logger)
}
