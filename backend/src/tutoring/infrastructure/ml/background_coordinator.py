"""Coalescing background training coordinator with debounce and single-worker execution."""

from __future__ import annotations

import concurrent.futures
from concurrent.futures import Future, ThreadPoolExecutor
import logging
import threading
import time

from tutoring.domain.ports.ml_training import TrainingTriggerPort
from tutoring.infrastructure.ml.trainer import (
    PedagogicalModelTrainer,
    TrainingReport,
    TrainingStatus,
)

logger = logging.getLogger(__name__)


class BackgroundTrainingCoordinator(TrainingTriggerPort):
    """Background coordinator coalescing training triggers using debouncing and burst threshold."""

    def __init__(
        self,
        trainer: PedagogicalModelTrainer,
        debounce_seconds: float = 5.0,
        burst_threshold: int = 10,
    ) -> None:
        if debounce_seconds < 0:
            raise ValueError("debounce_seconds must be non-negative")
        if burst_threshold < 1:
            raise ValueError("burst_threshold must be at least 1")

        self._trainer = trainer
        self._debounce_seconds = float(debounce_seconds)
        self._burst_threshold = int(burst_threshold)

        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml-trainer")
        self._state_lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._pending_events = 0
        self._in_flight = False
        self._dirty_while_in_flight = False
        self._current_future: Future[TrainingReport] | None = None
        self._last_report: TrainingReport | None = None
        self._shutdown = False
        self._timer_generation = 0

    @property
    def pending_events(self) -> int:
        """Return count of coalesced events waiting for debounce window to fire."""
        with self._state_lock:
            return self._pending_events

    @property
    def is_training(self) -> bool:
        """Return whether an asynchronous training job is currently in flight."""
        with self._state_lock:
            return self._in_flight

    @property
    def last_report(self) -> TrainingReport | None:
        """Return diagnostic report from the most recent training execution, if any."""
        with self._state_lock:
            return self._last_report

    def notify_new_data(self) -> None:
        """Signal that new training data was written and coalesce execution."""
        with self._state_lock:
            if self._shutdown:
                return

            self._pending_events += 1
            if self._in_flight:
                self._dirty_while_in_flight = True
                return

            if self._pending_events >= self._burst_threshold or self._debounce_seconds == 0:
                self._cancel_timer_locked()
                self._submit_job_locked()
            else:
                self._cancel_timer_locked()
                self._schedule_timer_locked()

    def flush(self, timeout: float = 30.0) -> TrainingReport | None:
        """Flush any pending or trailing dirty cycles, blocking until completion or timeout."""
        if timeout < 0:
            raise ValueError("timeout must be non-negative")

        deadline = time.monotonic() + timeout
        while True:
            with self._state_lock:
                if self._shutdown:
                    return self._last_report

                if not self._in_flight:
                    if self._pending_events > 0 or self._dirty_while_in_flight:
                        self._cancel_timer_locked()
                        self._submit_job_locked()
                    else:
                        return self._last_report

                future = self._current_future

            if future is None:
                return self._last_report

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return self._last_report

            try:
                future.result(timeout=remaining)
            except concurrent.futures.TimeoutError:
                return self._last_report
            except Exception:
                return self._last_report

    def shutdown(self, wait: bool = False) -> None:
        """Cancel pending debounce timers and shut down worker executor."""
        with self._state_lock:
            self._shutdown = True
            self._cancel_timer_locked()
            self._pending_events = 0
            self._dirty_while_in_flight = False

        self._executor.shutdown(wait=wait)

    def _cancel_timer_locked(self) -> None:
        self._timer_generation += 1
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _schedule_timer_locked(self) -> None:
        self._timer_generation += 1
        gen = self._timer_generation
        timer = threading.Timer(self._debounce_seconds, self._on_timer, args=(gen,))
        timer.daemon = True
        self._timer = timer
        timer.start()

    def _submit_job_locked(self) -> None:
        self._in_flight = True
        self._dirty_while_in_flight = False
        self._pending_events = 0
        self._current_future = self._executor.submit(self._run_job)

    def _on_timer(self, generation: int) -> None:
        with self._state_lock:
            if generation != self._timer_generation:
                return
            self._timer = None
            if self._shutdown or self._pending_events == 0:
                return
            if self._in_flight:
                self._dirty_while_in_flight = True
                return
            self._submit_job_locked()

    def _run_job(self) -> TrainingReport:
        report: TrainingReport | None = None
        try:
            try:
                report = self._trainer.train_and_activate()
            except Exception as exc:
                logger.exception("Pedagogical model training failed in background coordinator: %s", exc)
                report = TrainingReport(
                    status=TrainingStatus.FAILED,
                    sample_count=0,
                    reason=str(exc),
                )
            return report
        finally:
            with self._state_lock:
                if report is not None:
                    self._last_report = report
                self._in_flight = False
                if not self._shutdown and self._dirty_while_in_flight:
                    self._dirty_while_in_flight = False
                    if self._pending_events >= self._burst_threshold or self._debounce_seconds == 0:
                        self._cancel_timer_locked()
                        self._submit_job_locked()
                    else:
                        self._cancel_timer_locked()
                        self._schedule_timer_locked()
