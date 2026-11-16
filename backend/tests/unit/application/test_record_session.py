"""Unit tests for T3.4: RecordSessionUseCase."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tutoring.application.dtos import ExerciseAttemptInputDTO, RecordSessionDTO
from tutoring.application.fakes import (
    FakeTrainingTrigger,
    InMemoryCatalogRepository,
    InMemorySessionRepository,
    InMemoryStudentRepository,
)
from tutoring.application.use_cases.record_session import RecordSessionUseCase
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import EntityNotFoundError


def test_record_session_validates_student_and_exercise_types_and_saves() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()

    use_case = RecordSessionUseCase(
        student_repo=student_repo,
        catalog_repo=catalog_repo,
        session_repo=session_repo,
    )

    student = Student(id=uuid4(), full_name="Laura", academic_level="1º ESO")
    student_repo.save(student)

    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Fracciones")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Suma")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex_type)

    # Missing student
    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            student_id=uuid4(),
            dto=RecordSessionDTO(
                occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
                duration_minutes=60,
            ),
        )

    # Missing exercise type
    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            student_id=student.id,
            dto=RecordSessionDTO(
                occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
                duration_minutes=60,
                attempts=(
                    ExerciseAttemptInputDTO(
                        exercise_type_id=uuid4(),
                        outcome=AttemptOutcome.FAILURE,
                        error_cause=ErrorCause.CALCULATION,
                    ),
                ),
            ),
        )

    # Valid session
    dto = RecordSessionDTO(
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        session_notes="Buena concentración",
        attempts=(
            ExerciseAttemptInputDTO(
                exercise_type_id=ex_type.id,
                outcome=AttemptOutcome.FAILURE,
                error_cause=ErrorCause.CALCULATION,
            ),
            ExerciseAttemptInputDTO(
                exercise_type_id=ex_type.id,
                outcome=AttemptOutcome.SUCCESS,
            ),
        ),
    )

    session_dto = use_case.execute(student_id=student.id, dto=dto)
    assert session_dto.student_id == student.id
    assert session_dto.duration_minutes == 60
    assert session_dto.failure_rate == 0.5
    assert len(session_dto.attempts) == 2
    assert session_dto.attempts[0].severity_weight == 1.0
    assert session_dto.attempts[1].severity_weight == 0.0

    sessions = use_case.list_student_sessions(student.id)
    assert len(sessions) == 1
    assert sessions[0].id == session_dto.id


def test_record_session_notifies_trigger_only_when_attempts_present() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    trigger = FakeTrainingTrigger()
    use_case = RecordSessionUseCase(
        student_repo=student_repo,
        catalog_repo=catalog_repo,
        session_repo=session_repo,
        training_trigger=trigger,
    )
    student = Student(id=uuid4(), full_name="Hugo", academic_level="3º ESO")
    student_repo.save(student)
    subject = Subject(id=uuid4(), name="Lengua")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Sintaxis")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Oraciones")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex_type)

    # Empty attempts -> does not trigger retraining
    use_case.execute(
        student.id,
        RecordSessionDTO(
            occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
            duration_minutes=30,
            attempts=(),
        ),
    )
    assert trigger.trigger_count == 0

    # Session with attempts -> notifies trigger
    use_case.execute(
        student.id,
        RecordSessionDTO(
            occurred_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
            duration_minutes=60,
            attempts=(ExerciseAttemptInputDTO(ex_type.id, AttemptOutcome.SUCCESS),),
        ),
    )
    assert trigger.trigger_count == 1

