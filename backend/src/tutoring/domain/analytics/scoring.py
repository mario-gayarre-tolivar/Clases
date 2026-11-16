"""Shared deterministic scoring primitives for pedagogical analytics and ML features."""

import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime

from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.enums import AttemptOutcome, ErrorCause, LearningTrend
from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.attempt import ExerciseAttempt


def validate_analytics_params(
    decay_lambda: float,
    exam_horizon_days: int,
    min_trend_attempts: int,
    trend_threshold: float = 0.0,
) -> None:
    """Validate common analytics hyperparameters."""
    if decay_lambda < 0.0:
        raise ValidationError("decay_lambda cannot be negative.")
    if exam_horizon_days < 0:
        raise ValidationError("exam_horizon_days cannot be negative.")
    if trend_threshold < 0.0:
        raise ValidationError("trend_threshold cannot be negative.")
    if min_trend_attempts < 2:
        raise ValidationError("min_trend_attempts must be at least 2.")


@dataclass(frozen=True)
class TimedAttempt:
    """An exercise attempt enriched with its session timestamp and recency weight."""

    occurred_at: datetime
    attempt: ExerciseAttempt
    recency_weight: float


def compute_recency_weight(
    occurred_at: datetime, reference_date: date, decay_lambda: float
) -> float:
    """Compute exponential recency weight w = exp(-lambda * max(0, days_elapsed))."""
    days_elapsed = max(0, (reference_date - occurred_at.date()).days)
    return math.exp(-decay_lambda * days_elapsed)


def compute_weighted_failure_rate(timed_attempts: Sequence[TimedAttempt]) -> float:
    """Compute recency-weighted failure severity rate in [0.0, 1.0]."""
    if not timed_attempts:
        return 0.0
    total_weight = sum(item.recency_weight for item in timed_attempts)
    if total_weight <= 0.0:
        return 0.0
    weighted_severity = sum(
        item.recency_weight * item.attempt.severity_weight() for item in timed_attempts
    )
    return weighted_severity / total_weight


def collect_timed_attempts(
    sessions: Sequence[TutoringSession],
    reference_date: date,
    decay_lambda: float,
) -> list[TimedAttempt]:
    """Flatten sessions into chronologically ordered TimedAttempt entries."""
    ordered_sessions = sorted(sessions, key=lambda session: session.occurred_at)
    timed: list[TimedAttempt] = []
    for session in ordered_sessions:
        weight = compute_recency_weight(session.occurred_at, reference_date, decay_lambda)
        for attempt in session.attempts:
            timed.append(
                TimedAttempt(
                    occurred_at=session.occurred_at,
                    attempt=attempt,
                    recency_weight=weight,
                )
            )
    return timed


def compute_dominant_error_cause(
    timed_attempts: Sequence[TimedAttempt],
) -> ErrorCause | None:
    """Return recency- and severity-weighted dominant error cause, or None."""
    scores: dict[ErrorCause, float] = defaultdict(float)
    for item in timed_attempts:
        cause = item.attempt.error_cause
        if item.attempt.outcome == AttemptOutcome.SUCCESS or cause is None:
            continue
        scores[cause] += item.recency_weight * item.attempt.severity_weight()
    if not scores:
        return None
    return min(scores.items(), key=lambda entry: (-entry[1], entry[0].value))[0]


def compute_failure_delta(
    timed_attempts: Sequence[TimedAttempt],
    min_attempts: int = 4,
) -> float | None:
    """Return (recent_mean_failure - previous_mean_failure) or None if insufficient."""
    if len(timed_attempts) < min_attempts:
        return None
    ordered = sorted(timed_attempts, key=lambda item: item.occurred_at)
    mid = len(ordered) // 2
    previous = ordered[:mid]
    recent = ordered[mid:]
    prev_mean = sum(item.attempt.severity_weight() for item in previous) / len(previous)
    recent_mean = sum(item.attempt.severity_weight() for item in recent) / len(recent)
    return recent_mean - prev_mean


def compute_learning_trend(
    timed_attempts: Sequence[TimedAttempt],
    threshold: float = 0.15,
    min_attempts: int = 4,
) -> LearningTrend:
    """Classify learning evolution by comparing recent vs previous attempt windows."""
    delta = compute_failure_delta(timed_attempts, min_attempts=min_attempts)
    if delta is None:
        return LearningTrend.INSUFFICIENT_DATA
    if delta <= -threshold:
        return LearningTrend.IMPROVING
    if delta >= threshold:
        return LearningTrend.REGRESSING
    return LearningTrend.STAGNANT
