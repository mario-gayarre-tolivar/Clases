"""Port contract for pedagogical analysis engines (deterministic or classical ML)."""

from collections.abc import Sequence
from datetime import date
from typing import Protocol

from tutoring.domain.entities.catalog import AcademicCatalogSnapshot
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.value_objects.diagnostic import StudentDiagnostic


class PedagogicalAnalyzerPort(Protocol):
    """Strategy interface decoupled from concrete heuristic or ML implementations."""

    def analyze(
        self,
        student: Student,
        sessions: Sequence[TutoringSession],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> StudentDiagnostic:
        """Analyze a student's memory and return explainable diagnostic insights."""
        ...
