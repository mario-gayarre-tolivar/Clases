"""FastAPI application factory, dependency wiring, and domain error handlers."""

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tutoring.application.dtos import (
    CatalogTreeDTO,
    CreateExamGoalDTO,
    CreateExerciseTypeDTO,
    CreateStudentDTO,
    CreateSubjectDTO,
    CreateTopicDTO,
    ExamGoalDTO,
    ExerciseAttemptInputDTO,
    ExerciseTypeDTO,
    RecordSessionDTO,
    SessionDTO,
    StudentDetailDTO,
    StudentDiagnosticDTO,
    StudentSummaryDTO,
    SubjectDTO,
    TopicDTO,
)
from tutoring.application.use_cases.generate_diagnostic import (
    GenerateStudentDiagnosticUseCase,
)
from tutoring.application.use_cases.manage_catalog import ManageCatalogUseCase
from tutoring.application.use_cases.manage_students import ManageStudentsUseCase
from tutoring.application.use_cases.record_session import RecordSessionUseCase
from tutoring.domain.analytics.heuristic_analyzer import HeuristicPedagogicalAnalyzer
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import (
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from tutoring.infrastructure.persistence.sqlite_catalog_repo import (
    SqliteCatalogRepository,
)
from tutoring.infrastructure.persistence.sqlite_db import init_sqlite_db
from tutoring.infrastructure.persistence.sqlite_session_repo import (
    SqliteSessionRepository,
)
from tutoring.infrastructure.persistence.sqlite_student_repo import (
    SqliteStudentRepository,
)


class CreateSubjectPayload(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""


class CreateTopicPayload(BaseModel):
    subject_id: UUID
    name: str = Field(min_length=1)


class CreateExerciseTypePayload(BaseModel):
    topic_id: UUID
    name: str = Field(min_length=1)
    description: str = ""


class CreateStudentPayload(BaseModel):
    full_name: str = Field(min_length=1)
    academic_level: str = Field(min_length=1)
    pedagogical_notes: str = ""


class CreateExamGoalPayload(BaseModel):
    subject_id: UUID
    title: str = Field(min_length=1)
    exam_date: date
    topic_ids: list[UUID] = Field(default_factory=list)


class ExerciseAttemptPayload(BaseModel):
    exercise_type_id: UUID
    outcome: AttemptOutcome
    error_cause: ErrorCause | None = None
    notes: str = ""


class RecordSessionPayload(BaseModel):
    occurred_at: datetime
    duration_minutes: int = Field(gt=0)
    session_notes: str = ""
    attempts: list[ExerciseAttemptPayload] = Field(default_factory=list)


def create_app(db_path: str = ":memory:") -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    conn = init_sqlite_db(db_path)
    catalog_repo = SqliteCatalogRepository(conn)
    student_repo = SqliteStudentRepository(conn)
    session_repo = SqliteSessionRepository(conn)
    analyzer = HeuristicPedagogicalAnalyzer()

    manage_catalog_uc = ManageCatalogUseCase(catalog_repo)
    manage_students_uc = ManageStudentsUseCase(student_repo, catalog_repo)
    record_session_uc = RecordSessionUseCase(student_repo, catalog_repo, session_repo)
    generate_diagnostic_uc = GenerateStudentDiagnosticUseCase(
        student_repo, catalog_repo, session_repo, analyzer
    )

    app = FastAPI(title="Tutoring Management & Pedagogical Memory API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateEntityError)
    async def duplicate_entity_handler(
        request: Request, exc: DuplicateEntityError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    # Catalog endpoints
    @app.get("/api/catalog", response_model=CatalogTreeDTO)
    async def get_catalog() -> CatalogTreeDTO:
        return manage_catalog_uc.get_catalog_tree()

    @app.post(
        "/api/catalog/subjects",
        response_model=SubjectDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_subject(payload: CreateSubjectPayload) -> SubjectDTO:
        return manage_catalog_uc.create_subject(
            CreateSubjectDTO(name=payload.name, description=payload.description)
        )

    @app.post(
        "/api/catalog/topics",
        response_model=TopicDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_topic(payload: CreateTopicPayload) -> TopicDTO:
        return manage_catalog_uc.create_topic(
            CreateTopicDTO(subject_id=payload.subject_id, name=payload.name)
        )

    @app.post(
        "/api/catalog/exercise-types",
        response_model=ExerciseTypeDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_exercise_type(
        payload: CreateExerciseTypePayload,
    ) -> ExerciseTypeDTO:
        return manage_catalog_uc.create_exercise_type(
            CreateExerciseTypeDTO(
                topic_id=payload.topic_id,
                name=payload.name,
                description=payload.description,
            )
        )

    # Student endpoints
    @app.get("/api/students", response_model=list[StudentSummaryDTO])
    async def list_students() -> tuple[StudentSummaryDTO, ...]:
        return manage_students_uc.list_students()

    @app.post(
        "/api/students",
        response_model=StudentDetailDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_student(payload: CreateStudentPayload) -> StudentDetailDTO:
        return manage_students_uc.create_student(
            CreateStudentDTO(
                full_name=payload.full_name,
                academic_level=payload.academic_level,
                pedagogical_notes=payload.pedagogical_notes,
            )
        )

    @app.get("/api/students/{student_id}", response_model=StudentDetailDTO)
    async def get_student(student_id: UUID) -> StudentDetailDTO:
        return manage_students_uc.get_student_detail(student_id)

    @app.post(
        "/api/students/{student_id}/exam-goals",
        response_model=ExamGoalDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def add_exam_goal(
        student_id: UUID, payload: CreateExamGoalPayload
    ) -> ExamGoalDTO:
        return manage_students_uc.add_exam_goal(
            student_id=student_id,
            dto=CreateExamGoalDTO(
                subject_id=payload.subject_id,
                title=payload.title,
                exam_date=payload.exam_date,
                topic_ids=tuple(payload.topic_ids),
            ),
            today=date.today(),
        )

    # Session endpoints
    @app.post(
        "/api/students/{student_id}/sessions",
        response_model=SessionDTO,
        status_code=status.HTTP_201_CREATED,
    )
    async def record_session(
        student_id: UUID, payload: RecordSessionPayload
    ) -> SessionDTO:
        return record_session_uc.execute(
            student_id=student_id,
            dto=RecordSessionDTO(
                occurred_at=payload.occurred_at,
                duration_minutes=payload.duration_minutes,
                session_notes=payload.session_notes,
                attempts=tuple(
                    ExerciseAttemptInputDTO(
                        exercise_type_id=a.exercise_type_id,
                        outcome=a.outcome,
                        error_cause=a.error_cause,
                        notes=a.notes,
                    )
                    for a in payload.attempts
                ),
            ),
        )

    @app.get(
        "/api/students/{student_id}/sessions",
        response_model=list[SessionDTO],
    )
    async def list_student_sessions(student_id: UUID) -> tuple[SessionDTO, ...]:
        return record_session_uc.list_student_sessions(student_id)

    # Diagnostic endpoint
    @app.get(
        "/api/students/{student_id}/diagnostic",
        response_model=StudentDiagnosticDTO,
    )
    async def get_student_diagnostic(
        student_id: UUID,
        reference_date: date | None = None,
    ) -> StudentDiagnosticDTO:
        ref_date = reference_date or date.today()
        return generate_diagnostic_uc.execute(
            student_id=student_id, reference_date=ref_date
        )

    return app
