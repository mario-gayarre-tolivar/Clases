"""Unit tests for T3.5: GenerateStudentDiagnosticUseCase."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from tutoring.application.dtos import ExerciseAttemptInputDTO, RecordSessionDTO
from tutoring.application.fakes import (
    InMemoryCatalogRepository,
    InMemorySessionRepository,
    InMemoryStudentRepository,
)
from tutoring.application.use_cases.generate_diagnostic import (
    GenerateStudentDiagnosticUseCase,
)
from tutoring.application.use_cases.record_session import RecordSessionUseCase
from tutoring.domain.analytics.heuristic_analyzer import HeuristicPedagogicalAnalyzer
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import EntityNotFoundError


def test_generate_student_diagnostic_orchestration() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    analyzer = HeuristicPedagogicalAnalyzer()

    use_case = GenerateStudentDiagnosticUseCase(
        student_repo=student_repo,
        catalog_repo=catalog_repo,
        session_repo=session_repo,
        analyzer=analyzer,
    )

    # Missing student raises
    with pytest.raises(EntityNotFoundError):
        use_case.execute(student_id=uuid4(), reference_date=date(2026, 11, 16))

    student = Student(id=uuid4(), full_name="Clara", academic_level="3º ESO")
    student_repo.save(student)

    subject = Subject(id=uuid4(), name="Física")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Fuerzas")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Rozamiento")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex_type)

    record_uc = RecordSessionUseCase(student_repo, catalog_repo, session_repo)
    record_uc.execute(
        student_id=student.id,
        dto=RecordSessionDTO(
            occurred_at=datetime(2026, 11, 16, 16, 0, tzinfo=timezone.utc),
            duration_minutes=45,
            attempts=(
                ExerciseAttemptInputDTO(
                    exercise_type_id=ex_type.id,
                    outcome=AttemptOutcome.FAILURE,
                    error_cause=ErrorCause.CONCEPT,
                ),
            ),
        ),
    )

    diagnostic = use_case.execute(student_id=student.id, reference_date=date(2026, 11, 16))

    assert diagnostic.student_id == student.id
    assert diagnostic.analyzer_name == "HeuristicPedagogicalAnalyzerV1"
    assert len(diagnostic.subject_priorities) == 1
    assert diagnostic.subject_priorities[0].subject_name == "Física"
    assert len(diagnostic.weak_exercise_types) == 1
    assert diagnostic.weak_exercise_types[0].exercise_type_name == "Rozamiento"
    assert diagnostic.weak_exercise_types[0].dominant_error_cause == ErrorCause.CONCEPT
