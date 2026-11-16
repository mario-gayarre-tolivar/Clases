"""Domain port interfaces."""

from tutoring.domain.ports.analyzer import PedagogicalAnalyzerPort
from tutoring.domain.ports.ml_training import TrainingTriggerPort
from tutoring.domain.ports.repositories import (
    CatalogRepository,
    SessionRepository,
    StudentRepository,
)

__all__ = [
    "CatalogRepository",
    "PedagogicalAnalyzerPort",
    "SessionRepository",
    "StudentRepository",
    "TrainingTriggerPort",
]
