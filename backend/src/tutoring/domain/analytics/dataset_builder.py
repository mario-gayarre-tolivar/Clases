"""Deterministic training dataset builder with hybrid labeling and anti-leakage guards."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date, timedelta
from uuid import UUID

from tutoring.domain.analytics.feature_extractor import FeatureExtractor
from tutoring.domain.entities.catalog import AcademicCatalogSnapshot
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.exceptions import EntityNotFoundError, ValidationError
from tutoring.domain.value_objects.exam_goal import ExamGoal


@dataclass(frozen=True)
class TrainingDataset:
    """Deterministic, immutable tabular dataset ready for ML model training and evaluation."""

    features: tuple[tuple[float, ...], ...]
    labels: tuple[int, ...]
    feature_names: tuple[str, ...]
    dataset_hash: str

    def __post_init__(self) -> None:
        if len(self.features) != len(self.labels):
            raise ValidationError(
                f"features and labels must have the same length, got {len(self.features)} features and {len(self.labels)} labels."
            )
        expected_len = len(self.feature_names)
        for i, row in enumerate(self.features):
            if len(row) != expected_len:
                raise ValidationError(
                    f"Each feature row must have the same length as feature_names ({expected_len}), but row {i} has {len(row)}."
                )
            for value in row:
                if not math.isfinite(value):
                    raise ValidationError(
                        f"Dataset feature must be finite, got {value}."
                    )
        for label in self.labels:
            if label not in (0, 1):
                raise ValidationError(
                    f"Dataset label must be 0 or 1, got {label}."
                )

    def __len__(self) -> int:
        return len(self.labels)


@dataclass(frozen=True)
class _CandidateCheckpoint:
    ref_date: date
    student: Student
    subject_id: UUID
    is_exam_checkpoint: bool
    exam_goals: tuple[ExamGoal, ...] = ()


def _build_pre_checkpoint_student(student: Student, ref_date: date) -> Student:
    masked_goals = [
        replace(g, result=None)
        if (g.exam_date >= ref_date and g.result is not None)
        else g
        for g in student.exam_goals
    ]
    return Student(
        id=student.id,
        full_name=student.full_name,
        academic_level=student.academic_level,
        pedagogical_notes=student.pedagogical_notes,
        exam_goals=masked_goals,
    )


def _compute_dataset_hash(
    feature_names: Sequence[str],
    features: Sequence[Sequence[float]],
    labels: Sequence[int],
) -> str:
    payload = {
        "feature_names": list(feature_names),
        "features": [
            [0.0 if abs(round(val, 8)) == 0.0 else round(val, 8) for val in row]
            for row in features
        ],
        "labels": list(labels),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class TrainingDatasetBuilder:
    """Builds deterministic, anti-leakage training datasets from pedagogical domain entities."""

    def __init__(
        self,
        feature_extractor: FeatureExtractor | None = None,
        failure_threshold: float = 0.40,
        exam_horizon_days: int = 14,
        max_samples: int = 5000,
    ) -> None:
        if not math.isfinite(failure_threshold) or not (0.0 <= failure_threshold <= 1.0):
            raise ValidationError(
                f"failure_threshold must be between 0.0 and 1.0, got {failure_threshold}."
            )
        if exam_horizon_days < 0:
            raise ValidationError(
                f"exam_horizon_days cannot be negative, got {exam_horizon_days}."
            )
        if max_samples <= 0:
            raise ValidationError(
                f"max_samples must be greater than zero, got {max_samples}."
            )

        self._failure_threshold = failure_threshold
        self._exam_horizon_days = exam_horizon_days
        self._max_samples = max_samples
        self._feature_extractor = (
            feature_extractor
            if feature_extractor is not None
            else FeatureExtractor(exam_horizon_days=exam_horizon_days)
        )

    @property
    def failure_threshold(self) -> float:
        return self._failure_threshold

    @property
    def exam_horizon_days(self) -> int:
        return self._exam_horizon_days

    @property
    def max_samples(self) -> int:
        return self._max_samples

    def build(
        self,
        students: Sequence[Student],
        sessions_by_student: Mapping[UUID, Sequence[TutoringSession]],
        catalog: AcademicCatalogSnapshot,
    ) -> TrainingDataset:
        """Construct a tabular TrainingDataset by extracting anti-leakage features and hybrid labels."""
        valid_subject_ids = {s.id for s in catalog.all_subjects()}

        exercise_to_subject: dict[UUID, UUID] = {}
        for ex in catalog.all_exercise_types():
            try:
                subject, _, _ = catalog.resolve_exercise_path(ex.id)
                exercise_to_subject[ex.id] = subject.id
            except EntityNotFoundError:
                continue

        candidates: list[_CandidateCheckpoint] = []
        exam_checkpoint_keys: set[tuple[UUID, UUID, date]] = set()

        # Step 2: Evaluated ExamGoal checkpoints
        for student in students:
            goals_by_subject_date: dict[tuple[UUID, date], list[ExamGoal]] = defaultdict(list)
            for goal in student.exam_goals:
                if goal.result is not None and goal.subject_id in valid_subject_ids:
                    goals_by_subject_date[(goal.subject_id, goal.exam_date)].append(goal)

            for (subject_id, exam_date), goals in goals_by_subject_date.items():
                key = (student.id, subject_id, exam_date)
                exam_checkpoint_keys.add(key)
                candidates.append(
                    _CandidateCheckpoint(
                        ref_date=exam_date,
                        student=student,
                        subject_id=subject_id,
                        is_exam_checkpoint=True,
                        exam_goals=tuple(goals),
                    )
                )

        # Step 3: Session checkpoints
        session_checkpoint_keys: set[tuple[UUID, UUID, date]] = set()
        for student in students:
            student_sessions = sessions_by_student.get(student.id, ())
            sessions_by_date: dict[date, list[TutoringSession]] = defaultdict(list)
            for session in student_sessions:
                sessions_by_date[session.occurred_at.date()].append(session)

            for session_date, day_sessions in sessions_by_date.items():
                day_subject_ids: set[UUID] = set()
                for s in day_sessions:
                    for att in s.attempts:
                        sub_id = exercise_to_subject.get(att.exercise_type_id)
                        if sub_id is not None:
                            day_subject_ids.add(sub_id)

                for subject_id in sorted(day_subject_ids, key=str):
                    key = (student.id, subject_id, session_date)
                    if key in exam_checkpoint_keys or key in session_checkpoint_keys:
                        continue
                    session_checkpoint_keys.add(key)
                    candidates.append(
                        _CandidateCheckpoint(
                            ref_date=session_date,
                            student=student,
                            subject_id=subject_id,
                            is_exam_checkpoint=False,
                        )
                    )

        # Sort chronologically by (ref_date, str(student.id), str(subject_id))
        candidates.sort(
            key=lambda cp: (cp.ref_date, str(cp.student.id), str(cp.subject_id))
        )

        # Retain the most recent max_samples entries
        if len(candidates) > self._max_samples:
            candidates = candidates[-self._max_samples:]

        feature_names = self._feature_extractor.FEATURE_NAMES
        weighted_failure_rate_idx = feature_names.index("weighted_failure_rate")

        features_list: list[tuple[float, ...]] = []
        labels_list: list[int] = []

        for cp in candidates:
            student_sessions = sessions_by_student.get(cp.student.id, ())
            filtered_sessions = [
                s for s in student_sessions if s.occurred_at.date() <= cp.ref_date
            ]
            student_view = _build_pre_checkpoint_student(cp.student, cp.ref_date)

            feature_vector = self._feature_extractor.extract_subject_features(
                student=student_view,
                subject_id=cp.subject_id,
                sessions=filtered_sessions,
                catalog=catalog,
                reference_date=cp.ref_date,
            )
            features_list.append(feature_vector.values)

            weighted_failure = feature_vector.values[weighted_failure_rate_idx]

            if cp.is_exam_checkpoint:
                is_failed_exam = any(
                    g.result is not None and not g.result.is_passing
                    for g in cp.exam_goals
                )
                label = (
                    1
                    if (is_failed_exam or weighted_failure > self._failure_threshold)
                    else 0
                )
            else:
                horizon_end = cp.ref_date + timedelta(days=self._exam_horizon_days)
                has_failing_future_exam = any(
                    g.subject_id == cp.subject_id
                    and g.result is not None
                    and not g.result.is_passing
                    and (cp.ref_date < g.exam_date <= horizon_end)
                    for g in cp.student.exam_goals
                )
                label = (
                    1
                    if (
                        weighted_failure > self._failure_threshold
                        or has_failing_future_exam
                    )
                    else 0
                )

            labels_list.append(label)

        features_tuple = tuple(features_list)
        labels_tuple = tuple(labels_list)
        dataset_hash = _compute_dataset_hash(
            feature_names, features_tuple, labels_tuple
        )

        return TrainingDataset(
            features=features_tuple,
            labels=labels_tuple,
            feature_names=feature_names,
            dataset_hash=dataset_hash,
        )
