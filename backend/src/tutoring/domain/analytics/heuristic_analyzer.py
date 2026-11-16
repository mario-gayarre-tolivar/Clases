"""Deterministic heuristic pedagogical analyzer (zero external LLM dependency)."""

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, datetime, timezone
from uuid import UUID

from tutoring.domain.analytics.scoring import (
    TimedAttempt,
    collect_timed_attempts,
    compute_dominant_error_cause,
    compute_learning_trend,
    compute_weighted_failure_rate,
    validate_analytics_params,
)
from tutoring.domain.entities.catalog import AcademicCatalogSnapshot
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import LearningTrend
from tutoring.domain.value_objects.diagnostic import (
    ExamAlert,
    StudentDiagnostic,
    SubjectPriority,
    WeakExerciseType,
)
from tutoring.domain.value_objects.exam_goal import ExamGoal

_RISK_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _evaluate_readiness_risk(
    attempts_count: int, failure_rate: float, days_remaining: int
) -> str:
    if attempts_count == 0 or failure_rate >= 0.6:
        return "HIGH"
    if days_remaining <= 3 and failure_rate >= 0.35:
        return "HIGH"
    if failure_rate >= 0.3 or days_remaining <= 7:
        return "MEDIUM"
    return "LOW"


def _compute_exam_urgency_bonus(
    upcoming_exam_days: int | None, horizon_days: int
) -> float:
    if upcoming_exam_days is None:
        return 0.0
    urgency_factor = (horizon_days + 1 - upcoming_exam_days) / (horizon_days + 1)
    return urgency_factor * 25.0


class HeuristicPedagogicalAnalyzer:
    """Rule-based and statistical pedagogical analyzer using recency decay and exam urgency."""

    ANALYZER_NAME = "HeuristicPedagogicalAnalyzerV1"

    def __init__(
        self,
        decay_lambda: float = 0.05,
        exam_horizon_days: int = 14,
        trend_threshold: float = 0.15,
        min_trend_attempts: int = 4,
    ) -> None:
        validate_analytics_params(
            decay_lambda=decay_lambda,
            exam_horizon_days=exam_horizon_days,
            min_trend_attempts=min_trend_attempts,
            trend_threshold=trend_threshold,
        )
        self._decay_lambda = decay_lambda
        self._exam_horizon_days = exam_horizon_days
        self._trend_threshold = trend_threshold
        self._min_trend_attempts = min_trend_attempts

    def analyze(
        self,
        student: Student,
        sessions: Sequence[TutoringSession],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> StudentDiagnostic:
        """Produce an explainable StudentDiagnostic from sessions, exam goals, and catalog."""
        generated_at = datetime(
            reference_date.year,
            reference_date.month,
            reference_date.day,
            tzinfo=timezone.utc,
        )
        timed_attempts = collect_timed_attempts(
            sessions, reference_date=reference_date, decay_lambda=self._decay_lambda
        )
        attempts_by_subject = self._group_attempts_by_subject(timed_attempts, catalog)
        upcoming_exams = student.upcoming_exams(
            reference_date, horizon_days=self._exam_horizon_days
        )
        exams_by_subject = self._group_exams_by_subject(upcoming_exams)

        subject_priorities = self._build_subject_priorities(
            attempts_by_subject, exams_by_subject, catalog, reference_date
        )
        exam_alerts = self._build_exam_alerts(
            upcoming_exams, attempts_by_subject, catalog, reference_date
        )
        weak_exercise_types = self._build_weak_exercise_types(
            timed_attempts, catalog
        )
        overall_trend = compute_learning_trend(
            timed_attempts,
            threshold=self._trend_threshold,
            min_attempts=self._min_trend_attempts,
        )

        return StudentDiagnostic(
            student_id=student.id,
            generated_at=generated_at,
            analyzer_name=self.ANALYZER_NAME,
            subject_priorities=subject_priorities,
            weak_exercise_types=weak_exercise_types,
            exam_alerts=exam_alerts,
            overall_trend=overall_trend,
        )

    def _group_attempts_by_subject(
        self,
        timed_attempts: Sequence[TimedAttempt],
        catalog: AcademicCatalogSnapshot,
    ) -> dict[UUID, list[TimedAttempt]]:
        grouped: dict[UUID, list[TimedAttempt]] = defaultdict(list)
        for item in timed_attempts:
            subject, _, _ = catalog.resolve_exercise_path(item.attempt.exercise_type_id)
            grouped[subject.id].append(item)
        return grouped

    def _group_exams_by_subject(
        self, upcoming_exams: Sequence[ExamGoal]
    ) -> dict[UUID, list[ExamGoal]]:
        grouped: dict[UUID, list[ExamGoal]] = defaultdict(list)
        for goal in upcoming_exams:
            grouped[goal.subject_id].append(goal)
        return grouped

    def _build_subject_priorities(
        self,
        attempts_by_subject: dict[UUID, list[TimedAttempt]],
        exams_by_subject: dict[UUID, list[ExamGoal]],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> tuple[SubjectPriority, ...]:
        candidate_subject_ids = set(attempts_by_subject.keys()) | set(
            exams_by_subject.keys()
        )
        priorities: list[SubjectPriority] = []
        for subject_id in candidate_subject_ids:
            subject = catalog.get_subject(subject_id)
            subject_attempts = attempts_by_subject.get(subject_id, [])
            subject_exams = exams_by_subject.get(subject_id, [])
            failure_rate = compute_weighted_failure_rate(subject_attempts)
            upcoming_days = (
                min(goal.days_remaining(reference_date) for goal in subject_exams)
                if subject_exams
                else None
            )
            base_score = failure_rate * 70.0
            exam_bonus = _compute_exam_urgency_bonus(
                upcoming_days, self._exam_horizon_days
            )
            subject_trend = compute_learning_trend(
                subject_attempts,
                threshold=self._trend_threshold,
                min_attempts=self._min_trend_attempts,
            )
            trend_bonus = 5.0 if subject_trend == LearningTrend.REGRESSING else 0.0
            score = round(min(100.0, max(0.0, base_score + exam_bonus + trend_bonus)), 2)

            reasons: list[str] = []
            if subject_attempts:
                reasons.append(
                    f"Tasa ponderada de fallo: {round(failure_rate * 100)}% "
                    f"({len(subject_attempts)} intentos)"
                )
            else:
                reasons.append("Sin práctica registrada todavía")
            if upcoming_days is not None:
                reasons.append(f"Examen próximo en {upcoming_days} días")
            if subject_trend == LearningTrend.REGRESSING:
                reasons.append("Tendencia en regresión reciente")
            elif subject_trend == LearningTrend.IMPROVING:
                reasons.append("Tendencia de mejora")

            priorities.append(
                SubjectPriority(
                    subject_id=subject.id,
                    subject_name=subject.name,
                    priority_score=score,
                    weighted_failure_rate=round(failure_rate, 4),
                    upcoming_exam_days=upcoming_days,
                    trend=subject_trend,
                    reasons=tuple(reasons),
                )
            )

        priorities.sort(
            key=lambda p: (-p.priority_score, -p.weighted_failure_rate, p.subject_name)
        )
        return tuple(priorities)

    def _build_exam_alerts(
        self,
        upcoming_exams: Sequence[ExamGoal],
        attempts_by_subject: dict[UUID, list[TimedAttempt]],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> tuple[ExamAlert, ...]:
        alerts: list[ExamAlert] = []
        for goal in upcoming_exams:
            subject = catalog.get_subject(goal.subject_id)
            subject_attempts = attempts_by_subject.get(goal.subject_id, [])
            failure_rate = compute_weighted_failure_rate(subject_attempts)
            days_remaining = goal.days_remaining(reference_date)
            risk = _evaluate_readiness_risk(
                len(subject_attempts), failure_rate, days_remaining
            )
            alerts.append(
                ExamAlert(
                    exam_goal_id=goal.id,
                    subject_name=subject.name,
                    title=goal.title,
                    days_remaining=days_remaining,
                    readiness_risk=risk,
                )
            )
        alerts.sort(
            key=lambda a: (a.days_remaining, _RISK_ORDER[a.readiness_risk], a.title)
        )
        return tuple(alerts)

    def _build_weak_exercise_types(
        self,
        timed_attempts: Sequence[TimedAttempt],
        catalog: AcademicCatalogSnapshot,
    ) -> tuple[WeakExerciseType, ...]:
        grouped: dict[UUID, list[TimedAttempt]] = defaultdict(list)
        for item in timed_attempts:
            grouped[item.attempt.exercise_type_id].append(item)

        weak_items: list[WeakExerciseType] = []
        for ex_id, ex_attempts in grouped.items():
            failure_rate = compute_weighted_failure_rate(ex_attempts)
            if failure_rate <= 0.0:
                continue
            subject, topic, ex_type = catalog.resolve_exercise_path(ex_id)
            weak_items.append(
                WeakExerciseType(
                    exercise_type_id=ex_type.id,
                    exercise_type_name=ex_type.name,
                    topic_name=topic.name,
                    subject_name=subject.name,
                    attempts_count=len(ex_attempts),
                    weighted_failure_rate=round(failure_rate, 4),
                    dominant_error_cause=compute_dominant_error_cause(ex_attempts),
                )
            )
        weak_items.sort(
            key=lambda w: (
                -w.weighted_failure_rate,
                -w.attempts_count,
                w.exercise_type_name,
            )
        )
        return tuple(weak_items)
