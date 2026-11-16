"""Integration tests for T4.4: SklearnPedagogicalAnalyzer."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from sklearn.tree import DecisionTreeClassifier

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
