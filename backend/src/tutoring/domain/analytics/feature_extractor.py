"""Deterministic feature extractor converting student memory into tabular ML vectors."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from tutoring.domain.analytics.scoring import (
    TimedAttempt,
    collect_timed_attempts,
    compute_failure_delta,
    compute_weighted_failure_rate,
    validate_analytics_params,
)
from tutoring.domain.entities.catalog import AcademicCatalogSnapshot
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.exam_goal import ExamGoal

_NO_DATA_DAYS = 999.0


@dataclass(frozen=True)
class FeatureVector:
    """Fixed-schema finite numeric feature vector ready for classical ML models."""

    feature_names: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.feature_names) != len(self.values):
            raise ValidationError(
                "feature_names and values must have the same length."
            )
        for name, value in zip(self.feature_names, self.values, strict=True):
            if not math.isfinite(value):
                raise ValidationError(f"Feature '{name}' must be finite, got {value}.")

    def to_dict(self) -> dict[str, float]:
        """Return mapping of feature name to float value."""
        return dict(zip(self.feature_names, self.values, strict=True))


class FeatureExtractor:
    """Extracts deterministic numeric features at student or subject granularity."""

    FEATURE_NAMES: tuple[str, ...] = (
        "sessions_count",
        "attempts_count",
        "weighted_failure_rate",
        "raw_failure_rate",
        "failure_trend_delta",
        "has_attempts",
        "days_since_last_session",
        "upcoming_exams_count",
        "min_days_to_upcoming_exam",
        "cause_concept_ratio",
        "cause_calculation_ratio",
        "cause_comprehension_ratio",
        "cause_carelessness_ratio",
    )

    def __init__(
        self,
        decay_lambda: float = 0.05,
        exam_horizon_days: int = 14,
        min_trend_attempts: int = 4,
    ) -> None:
        validate_analytics_params(
            decay_lambda=decay_lambda,
            exam_horizon_days=exam_horizon_days,
            min_trend_attempts=min_trend_attempts,
        )
        self._decay_lambda = decay_lambda
        self._exam_horizon_days = exam_horizon_days
        self._min_trend_attempts = min_trend_attempts

    def extract_student_features(
        self,
        student: Student,
        sessions: Sequence[TutoringSession],
        reference_date: date,
    ) -> FeatureVector:
        """Extract overall numeric feature vector for a student."""
        timed_attempts = collect_timed_attempts(
            sessions, reference_date=reference_date, decay_lambda=self._decay_lambda
        )
        upcoming_exams = student.upcoming_exams(
            reference_date, horizon_days=self._exam_horizon_days
        )
        last_session_date = max(
            (session.occurred_at.date() for session in sessions), default=None
        )
        return self._build_feature_vector(
            sessions_count=len(sessions),
            timed_attempts=timed_attempts,
            upcoming_exams=upcoming_exams,
            last_session_date=last_session_date,
            reference_date=reference_date,
        )

    def extract_subject_features(
        self,
        student: Student,
        subject_id: UUID,
        sessions: Sequence[TutoringSession],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> FeatureVector:
        """Extract numeric feature vector scoped to a specific subject."""
        catalog.get_subject(subject_id)
        scoped_sessions: list[TutoringSession] = []
        for session in sessions:
            matching_attempts = [
                attempt
                for attempt in session.attempts
                if catalog.resolve_exercise_path(attempt.exercise_type_id)[0].id
                == subject_id
            ]
            if matching_attempts:
                scoped_sessions.append(
                    TutoringSession(
                        id=session.id,
                        student_id=session.student_id,
                        occurred_at=session.occurred_at,
                        duration_minutes=session.duration_minutes,
                        session_notes=session.session_notes,
                        attempts=matching_attempts,
                    )
                )

        timed_attempts = collect_timed_attempts(
            scoped_sessions,
            reference_date=reference_date,
            decay_lambda=self._decay_lambda,
        )
        upcoming_exams = [
            goal
            for goal in student.upcoming_exams(
                reference_date, horizon_days=self._exam_horizon_days
            )
            if goal.subject_id == subject_id
        ]
        last_session_date = max(
            (session.occurred_at.date() for session in scoped_sessions), default=None
        )
        return self._build_feature_vector(
            sessions_count=len(scoped_sessions),
            timed_attempts=timed_attempts,
            upcoming_exams=upcoming_exams,
            last_session_date=last_session_date,
            reference_date=reference_date,
        )

    def _build_feature_vector(
        self,
        sessions_count: int,
        timed_attempts: Sequence[TimedAttempt],
        upcoming_exams: Sequence[ExamGoal],
        last_session_date: date | None,
        reference_date: date,
    ) -> FeatureVector:
        attempts_count = len(timed_attempts)
        weighted_failure = compute_weighted_failure_rate(timed_attempts)
        raw_failure = (
            sum(item.attempt.severity_weight() for item in timed_attempts)
            / attempts_count
            if attempts_count > 0
            else 0.0
        )
        raw_delta = compute_failure_delta(
            timed_attempts, min_attempts=self._min_trend_attempts
        )
        trend_delta = 0.0 if raw_delta is None else raw_delta
        has_attempts = 1.0 if attempts_count > 0 else 0.0
        days_since_last = (
            float(max(0, (reference_date - last_session_date).days))
            if last_session_date is not None
            else _NO_DATA_DAYS
        )
        exams_count = float(len(upcoming_exams))
        min_exam_days = (
            float(min(goal.days_remaining(reference_date) for goal in upcoming_exams))
            if upcoming_exams
            else _NO_DATA_DAYS
        )
        cause_ratios = self._compute_cause_ratios(timed_attempts)

        values = (
            float(sessions_count),
            float(attempts_count),
            weighted_failure,
            raw_failure,
            trend_delta,
            has_attempts,
            days_since_last,
            exams_count,
            min_exam_days,
            cause_ratios[ErrorCause.CONCEPT],
            cause_ratios[ErrorCause.CALCULATION],
            cause_ratios[ErrorCause.COMPREHENSION],
            cause_ratios[ErrorCause.CARELESSNESS],
        )
        return FeatureVector(feature_names=self.FEATURE_NAMES, values=values)

    @staticmethod
    def _compute_cause_ratios(
        timed_attempts: Sequence[TimedAttempt],
    ) -> dict[ErrorCause, float]:
        counts: dict[ErrorCause, int] = {cause: 0 for cause in ErrorCause}
        non_success_total = 0
        for item in timed_attempts:
            if item.attempt.outcome == AttemptOutcome.SUCCESS:
                continue
            non_success_total += 1
            if item.attempt.error_cause is not None:
                counts[item.attempt.error_cause] += 1
        if non_success_total == 0:
            return {cause: 0.0 for cause in ErrorCause}
        return {
            cause: counts[cause] / non_success_total for cause in ErrorCause
        }
