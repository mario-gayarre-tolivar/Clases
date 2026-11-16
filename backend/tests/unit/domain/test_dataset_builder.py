from datetime import date, datetime, timezone
import math
import pytest
from uuid import uuid4

from tutoring.domain.analytics.dataset_builder import (
    TrainingDataset,
    TrainingDatasetBuilder,
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
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult


def test_dataset_builder_applies_hybrid_labeling_and_prevents_future_leakage() -> None:
    math_subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math_subject.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math_subject], topics=[topic], exercise_types=[ex])

    exam_date = date(2026, 11, 10)
    failed_goal = ExamGoal(
        id=uuid4(),
        subject_id=math_subject.id,
        title="Parcial 1",
        exam_date=exam_date,
        result=ExamResult(score=4.5, recorded_at=datetime(2026, 11, 11, 10, 0, tzinfo=timezone.utc)),
    )
    student = Student(id=uuid4(), full_name="Hugo", academic_level="4º ESO", exam_goals=[failed_goal])

    # Pre-exam session has LOW failure (0.0) -> still labeled 1 because exam failed (< 5.0)
    s_before = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 5, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
    )
    # Post-exam session on Nov 15 with HIGH failure (1.0) must NOT leak into Nov 10 checkpoint
    s_after = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 15, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT)],
    )

    builder = TrainingDatasetBuilder()
    dataset = builder.build([student], {student.id: [s_before, s_after]}, catalog)

    # Checkpoints: Nov 5 (session before failing exam within 14d -> 1), Nov 10 (exam -> 1, sessions_count=1.0), Nov 15 (session failure>0.4 -> 1)
    assert len(dataset.features) == 3
    assert dataset.labels == (1, 1, 1)
    sessions_count_idx = dataset.feature_names.index("sessions_count")
    # Nov 10 exam checkpoint must see only 1 session (s_before), not s_after
    assert dataset.features[1][sessions_count_idx] == 1.0


def test_dataset_builder_labels_normal_when_passing_and_low_failure_and_ignores_empty_sessions() -> None:
    math_subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math_subject.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math_subject], topics=[topic], exercise_types=[ex])

    passed_goal = ExamGoal(
        id=uuid4(),
        subject_id=math_subject.id,
        title="Parcial 1",
        exam_date=date(2026, 11, 10),
        result=ExamResult(score=8.0, recorded_at=datetime(2026, 11, 10, 19, 0, tzinfo=timezone.utc)),
    )
    student = Student(id=uuid4(), full_name="Alba", academic_level="1º Bach", exam_goals=[passed_goal])

    s_same_day = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
    )
    s_empty = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc),
        duration_minutes=30,
        attempts=[],
    )

    builder = TrainingDatasetBuilder()
    ds_without_empty = builder.build([student], {student.id: [s_same_day]}, catalog)
    ds_with_empty = builder.build([student], {student.id: [s_same_day, s_empty]}, catalog)

    # Deduplicated on Nov 10 -> 1 sample, labeled 0; empty session produces no change
    assert len(ds_without_empty.features) == 1
    assert ds_without_empty.labels == (0,)
    assert ds_without_empty.dataset_hash == ds_with_empty.dataset_hash


def test_dataset_builder_respects_max_samples_cap() -> None:
    math_subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math_subject.id, name="Aritmética")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Sumas")
    catalog = AcademicCatalogSnapshot(subjects=[math_subject], topics=[topic], exercise_types=[ex])
    student = Student(id=uuid4(), full_name="Leo", academic_level="1º ESO")
    sessions = [
        TutoringSession(
            id=uuid4(),
            student_id=student.id,
            occurred_at=datetime(2026, 11, day, 17, 0, tzinfo=timezone.utc),
            duration_minutes=45,
            attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
        )
        for day in range(1, 11)
    ]

    dataset = TrainingDatasetBuilder(max_samples=4).build([student], {student.id: sessions}, catalog)
    assert len(dataset.features) == 4


def test_dataset_builder_validates_hyperparameters() -> None:
    with pytest.raises(ValidationError, match="failure_threshold"):
        TrainingDatasetBuilder(failure_threshold=-0.1)

    with pytest.raises(ValidationError, match="failure_threshold"):
        TrainingDatasetBuilder(failure_threshold=1.5)

    with pytest.raises(ValidationError, match="failure_threshold"):
        TrainingDatasetBuilder(failure_threshold=math.nan)

    with pytest.raises(ValidationError, match="exam_horizon_days"):
        TrainingDatasetBuilder(exam_horizon_days=-1)

    with pytest.raises(ValidationError, match="max_samples"):
        TrainingDatasetBuilder(max_samples=0)


def test_training_dataset_validates_invariants() -> None:
    with pytest.raises(ValidationError, match="features and labels must have the same length"):
        TrainingDataset(
            features=((1.0, 2.0),),
            labels=(0, 1),
            feature_names=("f1", "f2"),
            dataset_hash="abc",
        )

    with pytest.raises(ValidationError, match="feature row must have the same length"):
        TrainingDataset(
            features=((1.0,),),
            labels=(0,),
            feature_names=("f1", "f2"),
            dataset_hash="abc",
        )

    with pytest.raises(ValidationError, match="Dataset feature must be finite"):
        TrainingDataset(
            features=((math.nan, 1.0),),
            labels=(0,),
            feature_names=("f1", "f2"),
            dataset_hash="abc",
        )

    with pytest.raises(ValidationError, match="Dataset label must be 0 or 1"):
        TrainingDataset(
            features=((1.0, 2.0),),
            labels=(2,),
            feature_names=("f1", "f2"),
            dataset_hash="abc",
        )


def test_dataset_builder_empty_inputs_returns_empty_dataset() -> None:
    catalog = AcademicCatalogSnapshot()
    builder = TrainingDatasetBuilder()
    dataset = builder.build([], {}, catalog)

    assert len(dataset.features) == 0
    assert len(dataset.labels) == 0
    assert len(dataset.feature_names) == 13
    assert isinstance(dataset.dataset_hash, str)
    assert len(dataset.dataset_hash) == 64


def test_dataset_builder_handles_subject_not_in_catalog() -> None:
    catalog = AcademicCatalogSnapshot()
    student = Student(
        id=uuid4(),
        full_name="Lucas",
        academic_level="2º Bach",
        exam_goals=[
            ExamGoal(
                id=uuid4(),
                subject_id=uuid4(),  # not in catalog
                title="Unknown Subject Exam",
                exam_date=date(2026, 11, 20),
                result=ExamResult(score=3.0, recorded_at=datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)),
            )
        ],
    )
    builder = TrainingDatasetBuilder()
    dataset = builder.build([student], {}, catalog)
    assert len(dataset.features) == 0


def test_dataset_builder_multisubject_sessions_emits_distinct_checkpoints() -> None:
    math_subject = Subject(id=uuid4(), name="Matemáticas")
    math_topic = Topic(id=uuid4(), subject_id=math_subject.id, name="Álgebra")
    math_ex = ExerciseType(id=uuid4(), topic_id=math_topic.id, name="Ecuaciones")

    phys_subject = Subject(id=uuid4(), name="Física")
    phys_topic = Topic(id=uuid4(), subject_id=phys_subject.id, name="Cinemática")
    phys_ex = ExerciseType(id=uuid4(), topic_id=phys_topic.id, name="MRU")

    catalog = AcademicCatalogSnapshot(
        subjects=[math_subject, phys_subject],
        topics=[math_topic, phys_topic],
        exercise_types=[math_ex, phys_ex],
    )

    student = Student(id=uuid4(), full_name="Elena", academic_level="1º Bach")
    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 8, 16, 0, tzinfo=timezone.utc),
        duration_minutes=90,
        attempts=[
            ExerciseAttempt(math_ex.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(phys_ex.id, AttemptOutcome.FAILURE, ErrorCause.CALCULATION),
        ],
    )

    builder = TrainingDatasetBuilder()
    dataset = builder.build([student], {student.id: [session]}, catalog)

    assert len(dataset.features) == 2
    # Math has SUCCESS -> 0, Physics has FAILURE -> 1
    # Checkpoints are sorted by (ref_date, str(student.id), str(subject.id))
    # Let's inspect the two rows
    assert 0 in dataset.labels
    assert 1 in dataset.labels
