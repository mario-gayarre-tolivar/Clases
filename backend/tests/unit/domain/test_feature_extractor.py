"""Unit tests for T2.6: Deterministic FeatureExtractor and FeatureVector."""

import math
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from tutoring.domain.analytics.feature_extractor import (
    FeatureExtractor,
    FeatureVector,
)
from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.exam_goal import ExamGoal


def test_feature_vector_validates_alignment_and_finiteness() -> None:
    with pytest.raises(ValidationError):
        FeatureVector(feature_names=("a", "b"), values=(1.0,))
    with pytest.raises(ValidationError):
        FeatureVector(feature_names=("a",), values=(float("nan"),))
    with pytest.raises(ValidationError):
        FeatureVector(feature_names=("a",), values=(float("inf"),))

    vec = FeatureVector(feature_names=("a", "b"), values=(1.0, 2.5))
    assert vec.to_dict() == {"a": 1.0, "b": 2.5}


def test_feature_extractor_handles_empty_student_cleanly() -> None:
    extractor = FeatureExtractor()
    student = Student(id=uuid4(), full_name="Nadia", academic_level="4º ESO")

    vec = extractor.extract_student_features(
        student=student,
        sessions=[],
        reference_date=date(2026, 11, 16),
    )

    assert vec.feature_names == FeatureExtractor.FEATURE_NAMES
    assert len(vec.values) == len(FeatureExtractor.FEATURE_NAMES)
    assert all(math.isfinite(v) for v in vec.values)

    features = vec.to_dict()
    assert features["sessions_count"] == 0.0
    assert features["attempts_count"] == 0.0
    assert features["has_attempts"] == 0.0
    assert features["weighted_failure_rate"] == 0.0
    assert features["days_since_last_session"] == 999.0
    assert features["min_days_to_upcoming_exam"] == 999.0


def test_feature_extractor_extracts_student_and_subject_vectors() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    t_math = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    t_phy = Topic(id=uuid4(), subject_id=physics.id, name="Óptica")
    ex_math = ExerciseType(id=uuid4(), topic_id=t_math.id, name="Ecuaciones")
    ex_phy = ExerciseType(id=uuid4(), topic_id=t_phy.id, name="Espejos")
    catalog = AcademicCatalogSnapshot(
        subjects=[math, physics],
        topics=[t_math, t_phy],
        exercise_types=[ex_math, ex_phy],
    )

    math_exam = ExamGoal(
        id=uuid4(),
        subject_id=math.id,
        title="Parcial Álgebra",
        exam_date=date(2026, 11, 21),  # 5 days
    )
    student = Student(
        id=uuid4(),
        full_name="Pablo",
        academic_level="1º Bach",
        exam_goals=[math_exam],
    )
    s1 = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 10, 17, 0, tzinfo=timezone.utc),  # 6 days ago
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
            ExerciseAttempt(ex_math.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
        ],
    )
    s2 = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 14, 17, 0, tzinfo=timezone.utc),  # 2 days ago
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.PARTIAL, ErrorCause.CALCULATION),
            ExerciseAttempt(ex_math.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.SUCCESS),
        ],
    )

    extractor = FeatureExtractor()
    student_vec = extractor.extract_student_features(student, [s1, s2], ref_date).to_dict()
    math_vec = extractor.extract_subject_features(
        student, math.id, [s1, s2], catalog, ref_date
    ).to_dict()
    physics_vec = extractor.extract_subject_features(
        student, physics.id, [s1, s2], catalog, ref_date
    ).to_dict()

    # Student aggregate
    assert student_vec["sessions_count"] == 2.0
    assert student_vec["attempts_count"] == 5.0
    assert student_vec["days_since_last_session"] == 2.0
    assert student_vec["upcoming_exams_count"] == 1.0
    assert student_vec["min_days_to_upcoming_exam"] == 5.0
    assert student_vec["failure_trend_delta"] < 0.0  # improved from 1.0 to 0.1667

    # Math scoped: 2 sessions, 4 attempts, 3 non-success (2 CONCEPT, 1 CALCULATION)
    assert math_vec["sessions_count"] == 2.0
    assert math_vec["attempts_count"] == 4.0
    assert math_vec["has_attempts"] == 1.0
    assert math_vec["cause_concept_ratio"] == pytest.approx(2 / 3)
    assert math_vec["cause_calculation_ratio"] == pytest.approx(1 / 3)
    assert math_vec["cause_comprehension_ratio"] == 0.0
    assert math_vec["min_days_to_upcoming_exam"] == 5.0

    # Physics scoped: only s2 had physics attempts (1 attempt, 0 errors, no physics exam)
    assert physics_vec["sessions_count"] == 1.0
    assert physics_vec["attempts_count"] == 1.0
    assert physics_vec["raw_failure_rate"] == 0.0
    assert physics_vec["upcoming_exams_count"] == 0.0
    assert physics_vec["min_days_to_upcoming_exam"] == 999.0
