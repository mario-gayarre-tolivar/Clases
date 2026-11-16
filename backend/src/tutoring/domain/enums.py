"""Domain enumerations for attempt outcomes, error causes, and trends."""

from enum import Enum


class AttemptOutcome(str, Enum):
    """Outcome classification for a single exercise attempt."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILURE = "FAILURE"

    def failure_weight(self) -> float:
        """Return normalized failure severity weight in [0.0, 1.0]."""
        weights = {
            AttemptOutcome.SUCCESS: 0.0,
            AttemptOutcome.PARTIAL: 0.5,
            AttemptOutcome.FAILURE: 1.0,
        }
        return weights[self]


class ErrorCause(str, Enum):
    """Pedagogical root cause behind a partial or failed attempt."""

    CONCEPT = "CONCEPT"
    CALCULATION = "CALCULATION"
    COMPREHENSION = "COMPREHENSION"
    CARELESSNESS = "CARELESSNESS"


class LearningTrend(str, Enum):
    """Evolution direction of a student's performance over time."""

    IMPROVING = "IMPROVING"
    STAGNANT = "STAGNANT"
    REGRESSING = "REGRESSING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
