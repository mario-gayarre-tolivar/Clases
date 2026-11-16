"""Integration tests for T4.4: SklearnPedagogicalAnalyzer."""

import threading
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sklearn.tree import DecisionTreeClassifier

from tutoring.domain.analytics.feature_extractor import FeatureExtractor
from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.infrastructure.ml.model_store import ModelArtifactStore, ModelMetadata
from tutoring.infrastructure.ml.sklearn_analyzer import SklearnPedagogicalAnalyzer


def test_sklearn_analyzer_fallback_when_untrained() -> None:
    analyzer = SklearnPedagogicalAnalyzer()
    assert analyzer.is_trained is False

    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex_type])
    student = Student(id=uuid4(), full_name="Sergio", academic_level="ESO")

    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex_type.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT)],
    )

    diagnostic = analyzer.analyze(
        student=student,
        sessions=[session],
        catalog=catalog,
        reference_date=date(2026, 11, 16),
    )

    # Untrained falls back to heuristic engine cleanly
    assert diagnostic.analyzer_name == "HeuristicPedagogicalAnalyzerV1"
    assert len(diagnostic.subject_priorities) == 1
    assert diagnostic.subject_priorities[0].subject_name == "Matemáticas"


def test_sklearn_analyzer_trained_inference() -> None:
    clf = DecisionTreeClassifier(random_state=42)
    analyzer = SklearnPedagogicalAnalyzer(classifier=clf)

    # Train on synthetic dummy features: 2 samples, 13 features each
    # Class 1 = High urgency/priority, Class 0 = Low
    x_train = [
        [1.0, 2.0, 0.9, 0.9, 0.2, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.0],
        [1.0, 2.0, 0.0, 0.0, -0.2, 1.0, 10.0, 0.0, 999.0, 0.0, 0.0, 0.0, 0.0],
    ]
    y_train = [1, 0]
    analyzer.fit(x_train, y_train)

    assert analyzer.is_trained is True

    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex_type])
    student = Student(id=uuid4(), full_name="Sergio", academic_level="ESO")

    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_type.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
            ExerciseAttempt(ex_type.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
        ],
    )

    diagnostic = analyzer.analyze(
        student=student,
        sessions=[session],
        catalog=catalog,
        reference_date=date(2026, 11, 16),
    )

    assert diagnostic.analyzer_name == "SklearnPedagogicalAnalyzerV1"
    assert len(diagnostic.subject_priorities) == 1
    top_subject = diagnostic.subject_priorities[0]
    assert any("Modelo ML clásico" in reason for reason in top_subject.reasons)


def test_model_store_atomic_roundtrip_and_lazy_load(tmp_path: Path) -> None:
    store = ModelArtifactStore(tmp_path)
    clf = DecisionTreeClassifier(random_state=42)
    x_train = [[1.0] * 13, [0.0] * 13]
    clf.fit(x_train, [1, 0])
    meta = ModelMetadata(
        version=1,
        trained_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        analyzer_name="SklearnPedagogicalAnalyzerV1",
        sample_count=20,
        positive_count=10,
        negative_count=10,
        cv_f1_macro=0.85,
        baseline_f1_macro=0.45,
        dataset_hash="abc123",
        feature_names=FeatureExtractor.FEATURE_NAMES,
    )
    store.save(clf, meta)
    assert (tmp_path / "active_analyzer.joblib").exists()
    assert (tmp_path / "active_analyzer_meta.json").exists()

    # Lazy-loads persisted model on demand
    reloaded_analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    assert reloaded_analyzer.is_trained is True
    assert reloaded_analyzer.metadata == meta
    assert store.load_metadata() == meta


def test_model_store_rejects_corrupted_or_mismatched_schema_and_falls_back(tmp_path: Path) -> None:
    store = ModelArtifactStore(tmp_path)
    (tmp_path / "active_analyzer.joblib").write_bytes(b"corrupt-bytes")
    (tmp_path / "active_analyzer_meta.json").write_text('{"bad": "json"}', encoding="utf-8")
    assert store.load() is None
    assert store.load_metadata() is None

    # Valid joblib but mismatched feature_names -> rejected
    clf = DecisionTreeClassifier(random_state=42).fit([[0.0] * 13, [1.0] * 13], [0, 1])
    bad_meta = ModelMetadata(
        version=1,
        trained_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        analyzer_name="SklearnPedagogicalAnalyzerV1",
        sample_count=2,
        positive_count=1,
        negative_count=1,
        cv_f1_macro=0.8,
        baseline_f1_macro=0.5,
        dataset_hash="h",
        feature_names=("legacy_only",),
    )
    store.save(clf, bad_meta)
    assert store.load() is None
    assert store.load_metadata() is None

    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    assert analyzer.is_trained is False


def test_sklearn_analyzer_thread_safe_concurrent_update() -> None:
    store_clf1 = DecisionTreeClassifier(random_state=42).fit([[0.0] * 13, [1.0] * 13], [0, 1])
    store_clf2 = DecisionTreeClassifier(random_state=42).fit([[0.0] * 13, [1.0] * 13], [1, 0])
    analyzer = SklearnPedagogicalAnalyzer(classifier=store_clf1)
    analyzer.fit([[0.0] * 13, [1.0] * 13], [0, 1])

    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex_type])
    student = Student(id=uuid4(), full_name="Sergio", academic_level="ESO")
    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex_type.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT)],
    )

    errors: list[Exception] = []

    def reader() -> None:
        try:
            for _ in range(50):
                diag = analyzer.analyze(student, [session], catalog, date(2026, 11, 16))
                assert diag is not None
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    def writer() -> None:
        try:
            for i in range(50):
                clf = store_clf2 if i % 2 == 0 else store_clf1
                analyzer.update_model(clf)
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    t1 = threading.Thread(target=reader)
    t2 = threading.Thread(target=writer)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    assert errors == []
