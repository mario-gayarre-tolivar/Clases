"""Integration tests for PedagogicalModelTrainer lifecycle, quality gating, and concurrency."""

import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from sklearn.dummy import DummyClassifier

from tutoring.application.fakes import (
    InMemoryCatalogRepository,
    InMemorySessionRepository,
    InMemoryStudentRepository,
)
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult
from tutoring.infrastructure.ml.model_store import ModelArtifactStore
from tutoring.infrastructure.ml.sklearn_analyzer import SklearnPedagogicalAnalyzer
from tutoring.infrastructure.ml.trainer import PedagogicalModelTrainer, TrainingStatus


def _seed_repos(n_per_class: int, include_high: bool = True) -> tuple[
    InMemoryStudentRepository, InMemorySessionRepository, InMemoryCatalogRepository
]:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex)

    base = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)
    classes = [0, 1] if include_high else [0]
    for cls in classes:
        student = Student(id=uuid4(), full_name=f"Alumno {cls}", academic_level="4º ESO")
        for idx in range(n_per_class):
            dt = base + timedelta(days=idx)
            outcome = AttemptOutcome.FAILURE if cls == 1 else AttemptOutcome.SUCCESS
            cause = ErrorCause.CONCEPT if cls == 1 else None
            session_repo.save(
                TutoringSession(
                    id=uuid4(),
                    student_id=student.id,
                    occurred_at=dt,
                    duration_minutes=60,
                    attempts=[ExerciseAttempt(ex.id, outcome, cause)],
                )
            )
            if idx % 3 == 0:
                student.add_exam_goal(
                    ExamGoal(
                        id=uuid4(),
                        subject_id=subject.id,
                        title=f"Exam {cls}-{idx}",
                        exam_date=dt.date(),
                        result=ExamResult(score=3.0 if cls == 1 else 8.5, recorded_at=dt),
                    ),
                    today=dt.date(),
                )
        student_repo.save(student)
    return student_repo, session_repo, catalog_repo


def test_trainer_skips_insufficient_and_single_class_datasets(tmp_path: Path) -> None:
    s_repo, sess_repo, cat_repo = _seed_repos(n_per_class=5, include_high=True)
    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    trainer = PedagogicalModelTrainer(s_repo, sess_repo, cat_repo, analyzer, store, min_samples=20)
    rep_small = trainer.train_and_activate()
    assert rep_small.status == TrainingStatus.SKIPPED_INSUFFICIENT_DATA
    assert analyzer.is_trained is False

    s_repo2, sess_repo2, cat_repo2 = _seed_repos(n_per_class=22, include_high=False)
    trainer2 = PedagogicalModelTrainer(s_repo2, sess_repo2, cat_repo2, analyzer, store, min_samples=20)
    rep_single = trainer2.train_and_activate()
    assert rep_single.status == TrainingStatus.SKIPPED_SINGLE_CLASS
    assert analyzer.is_trained is False


def test_trainer_trains_persists_skips_unchanged_and_rejects_poor_quality(tmp_path: Path) -> None:
    s_repo, sess_repo, cat_repo = _seed_repos(n_per_class=12, include_high=True)  # 24 samples
    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    trainer = PedagogicalModelTrainer(s_repo, sess_repo, cat_repo, analyzer, store, min_samples=20)

    rep1 = trainer.train_and_activate()
    assert rep1.status == TrainingStatus.TRAINED
    assert rep1.model_version == 1
    assert rep1.cv_f1_macro is not None and rep1.baseline_f1_macro is not None
    assert rep1.cv_f1_macro > rep1.baseline_f1_macro
    assert analyzer.is_trained is True

    # Re-running with identical data short-circuits without retraining
    rep2 = trainer.train_and_activate()
    assert rep2.status == TrainingStatus.SKIPPED_UNCHANGED

    # Poor quality candidate (DummyClassifier) gets rejected and keeps version 1 intact
    poor_trainer = PedagogicalModelTrainer(
        s_repo,
        sess_repo,
        cat_repo,
        analyzer,
        store,
        min_samples=20,
        estimator_factory=lambda: DummyClassifier(strategy="most_frequent"),
    )
    # Bump dataset slightly by adding 1 new session to avoid hash short-circuit
    student = list(s_repo.list_all())[0]
    ex_id = cat_repo.get_snapshot().all_exercise_types()[0].id
    sess_repo.save(
        TutoringSession(
            id=uuid4(),
            student_id=student.id,
            occurred_at=datetime(2026, 11, 20, 17, 0, tzinfo=timezone.utc),
            duration_minutes=60,
            attempts=[ExerciseAttempt(ex_id, AttemptOutcome.SUCCESS)],
        )
    )
    rep_rejected = poor_trainer.train_and_activate()
    assert rep_rejected.status == TrainingStatus.REJECTED_QUALITY
    assert analyzer.metadata is not None and analyzer.metadata.version == 1


def test_trainer_skips_when_minority_class_below_cv_folds(tmp_path: Path) -> None:
    # 20 samples total, but only 2 in minority class with cv_folds=3
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex)

    base = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)
    student0 = Student(id=uuid4(), full_name="Alumno 0", academic_level="4º ESO")
    for idx in range(18):
        dt = base + timedelta(days=idx)
        session_repo.save(
            TutoringSession(
                id=uuid4(),
                student_id=student0.id,
                occurred_at=dt,
                duration_minutes=60,
                attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
            )
        )
    student_repo.save(student0)

    student1 = Student(id=uuid4(), full_name="Alumno 1", academic_level="4º ESO")
    for idx in range(2):
        dt = base + timedelta(days=idx)
        session_repo.save(
            TutoringSession(
                id=uuid4(),
                student_id=student1.id,
                occurred_at=dt,
                duration_minutes=60,
                attempts=[ExerciseAttempt(ex.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT)],
            )
        )
    student_repo.save(student1)

    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    trainer = PedagogicalModelTrainer(
        student_repo, session_repo, catalog_repo, analyzer, store, min_samples=20, cv_folds=3
    )
    rep = trainer.train_and_activate()
    assert rep.status == TrainingStatus.SKIPPED_INSUFFICIENT_DATA
    assert "cv_folds" in rep.reason or "minority" in rep.reason.lower()


def test_trainer_acquires_db_lock_only_during_fetch(tmp_path: Path) -> None:
    s_repo, sess_repo, cat_repo = _seed_repos(n_per_class=12, include_high=True)
    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)

    lock_events: list[str] = []

    class SpyRLock:
        def __init__(self) -> None:
            self._real_lock = threading.RLock()

        def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
            lock_events.append("acquire")
            return self._real_lock.acquire(blocking, timeout)

        def release(self) -> None:
            lock_events.append("release")
            self._real_lock.release()

        def __enter__(self) -> Any:
            self.acquire()
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            self.release()

    spy_lock: Any = SpyRLock()
    trainer = PedagogicalModelTrainer(
        s_repo, sess_repo, cat_repo, analyzer, store, min_samples=20, db_lock=spy_lock
    )

    rep = trainer.train_and_activate()
    assert rep.status == TrainingStatus.TRAINED
    # Lock was acquired and released exactly once during data fetch
    assert lock_events == ["acquire", "release"]
