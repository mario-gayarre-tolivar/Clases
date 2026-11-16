import threading
import time
import pytest
from tutoring.infrastructure.ml.background_coordinator import BackgroundTrainingCoordinator
from tutoring.infrastructure.ml.trainer import TrainingReport, TrainingStatus


class _StubTrainer:
    def __init__(self, fail: bool = False, wait_for_release: bool = False) -> None:
        self.calls = 0
        self._fail = fail
        self._wait_for_release = wait_for_release
        self.started_event = threading.Event()
        self.release_event = threading.Event()

    def train_and_activate(self) -> TrainingReport:
        self.calls += 1
        self.started_event.set()
        if self._wait_for_release and self.calls == 1:
            self.release_event.wait(timeout=2.0)
        if self._fail:
            raise RuntimeError("boom")
        return TrainingReport(status=TrainingStatus.TRAINED, sample_count=20, model_version=self.calls)


def test_coordinator_coalesces_events_within_debounce_window() -> None:
    trainer = _StubTrainer()
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=0.08, burst_threshold=10)  # type: ignore[arg-type]
    try:
        for _ in range(5):
            coord.notify_new_data()
        assert coord.pending_events == 5
        time.sleep(0.25)
        assert trainer.calls == 1
        assert coord.last_report is not None
        assert coord.last_report.status == TrainingStatus.TRAINED
    finally:
        coord.shutdown(wait=True)


def test_coordinator_triggers_immediately_on_burst_threshold_and_handles_errors() -> None:
    trainer = _StubTrainer(fail=True)
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=30.0, burst_threshold=3)  # type: ignore[arg-type]
    try:
        coord.notify_new_data()
        coord.notify_new_data()
        assert trainer.calls == 0
        coord.notify_new_data()  # hits burst_threshold=3
        report = coord.flush(timeout=2.0)
        assert trainer.calls == 1
        assert report is not None
        assert report.status == TrainingStatus.FAILED
    finally:
        coord.shutdown(wait=True)


def test_coordinator_coalesces_events_arriving_while_in_flight() -> None:
    trainer = _StubTrainer(wait_for_release=True)
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=0.05, burst_threshold=10)  # type: ignore[arg-type]
    try:
        coord.notify_new_data()
        assert trainer.started_event.wait(timeout=2.0)
        # Multiple events while job 1 is running coalesce into a single follow-up run
        for _ in range(4):
            coord.notify_new_data()
        trainer.release_event.set()
        time.sleep(0.2)
        assert trainer.calls == 2
    finally:
        coord.shutdown(wait=True)


def test_coordinator_parameter_validation() -> None:
    trainer = _StubTrainer()
    with pytest.raises(ValueError, match="debounce_seconds"):
        BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=-1.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="burst_threshold"):
        BackgroundTrainingCoordinator(trainer=trainer, burst_threshold=0)  # type: ignore[arg-type]


def test_coordinator_flush_with_no_pending_work() -> None:
    trainer = _StubTrainer()
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=1.0)  # type: ignore[arg-type]
    try:
        assert coord.pending_events == 0
        assert coord.is_training is False
        assert coord.last_report is None
        report = coord.flush(timeout=1.0)
        assert report is None
        assert trainer.calls == 0
    finally:
        coord.shutdown(wait=True)


def test_coordinator_shutdown_ignores_notifications_and_cancels_timer() -> None:
    trainer = _StubTrainer()
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=0.2)  # type: ignore[arg-type]
    coord.notify_new_data()
    coord.shutdown(wait=True)
    coord.notify_new_data()
    time.sleep(0.3)
    assert trainer.calls == 0
    assert coord.pending_events == 0
