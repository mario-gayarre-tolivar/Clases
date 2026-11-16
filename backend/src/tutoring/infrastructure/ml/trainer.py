"""Resource-bounded classical ML model trainer with cross-validation quality gating."""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import threading
from typing import Any

from sklearn.dummy import DummyClassifier  # type: ignore[import-untyped]
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.model_selection import StratifiedKFold, cross_val_score  # type: ignore[import-untyped]

from tutoring.domain.analytics.dataset_builder import TrainingDatasetBuilder
from tutoring.domain.ports.repositories import (
    CatalogRepository,
    SessionRepository,
    StudentRepository,
)
from tutoring.infrastructure.ml.model_store import ModelArtifactStore, ModelMetadata
from tutoring.infrastructure.ml.sklearn_analyzer import SklearnPedagogicalAnalyzer


class TrainingStatus(str, Enum):
    """Execution status outcomes for pedagogical model training pipeline."""

    TRAINED = "trained"
    SKIPPED_INSUFFICIENT_DATA = "skipped_insufficient_data"
    SKIPPED_SINGLE_CLASS = "skipped_single_class"
    SKIPPED_UNCHANGED = "skipped_unchanged"
    REJECTED_QUALITY = "rejected_quality"
    FAILED = "failed"


@dataclass(frozen=True)
class TrainingReport:
    """Diagnostic outcome report produced by PedagogicalModelTrainer."""

    status: TrainingStatus
    sample_count: int
    cv_f1_macro: float | None = None
    baseline_f1_macro: float | None = None
    model_version: int | None = None
    reason: str = ""


def _default_estimator() -> Any:
    return RandomForestClassifier(
        n_estimators=50,
        max_depth=5,
        min_samples_leaf=2,
        n_jobs=1,
        random_state=42,
    )


class PedagogicalModelTrainer:
    """Resource-bounded ML model trainer orchestrating CV evaluation and atomic deployment."""

    def __init__(
        self,
        student_repo: StudentRepository,
        session_repo: SessionRepository,
        catalog_repo: CatalogRepository,
        analyzer: SklearnPedagogicalAnalyzer,
        model_store: ModelArtifactStore,
        min_samples: int = 20,
        cv_folds: int = 3,
        min_f1_score: float = 0.55,
        estimator_factory: Callable[[], Any] | None = None,
        db_lock: threading.RLock | None = None,
        dataset_builder: TrainingDatasetBuilder | None = None,
    ) -> None:
        self._student_repo = student_repo
        self._session_repo = session_repo
        self._catalog_repo = catalog_repo
        self._analyzer = analyzer
        self._model_store = model_store
        self._min_samples = min_samples
        self._cv_folds = cv_folds
        self._min_f1_score = min_f1_score
        self._estimator_factory = estimator_factory
        self._db_lock = db_lock
        self._dataset_builder = dataset_builder or TrainingDatasetBuilder()

    def train_and_activate(self) -> TrainingReport:
        """Execute the full training pipeline with quality gating and atomic activation."""
        # Step 1: Fetch domain aggregates holding db_lock only during queries
        if self._db_lock is not None:
            with self._db_lock:
                students = self._student_repo.list_all()
                sessions_by_student = {
                    student.id: self._session_repo.list_by_student(student.id)
                    for student in students
                }
                catalog = self._catalog_repo.get_snapshot()
        else:
            students = self._student_repo.list_all()
            sessions_by_student = {
                student.id: self._session_repo.list_by_student(student.id)
                for student in students
            }
            catalog = self._catalog_repo.get_snapshot()

        # Step 2: Extract features and hybrid ground truth outside db_lock
        dataset = self._dataset_builder.build(students, sessions_by_student, catalog)
        sample_count = len(dataset)
        labels = dataset.labels
        features = dataset.features

        # Step 3: Validate sample size sufficiency
        if sample_count < self._min_samples:
            return TrainingReport(
                status=TrainingStatus.SKIPPED_INSUFFICIENT_DATA,
                sample_count=sample_count,
                reason=(
                    f"Dataset contains {sample_count} samples, which is below "
                    f"min_samples threshold of {self._min_samples}."
                ),
            )

        # Step 4: Validate class distribution and folds
        counts = Counter(labels)
        if len(counts) < 2:
            return TrainingReport(
                status=TrainingStatus.SKIPPED_SINGLE_CLASS,
                sample_count=sample_count,
                reason="Dataset contains only a single class; binary classification requires at least 2.",
            )

        min_class_samples = min(counts.values())
        if min_class_samples < self._cv_folds:
            return TrainingReport(
                status=TrainingStatus.SKIPPED_INSUFFICIENT_DATA,
                sample_count=sample_count,
                reason=(
                    f"Minority class has only {min_class_samples} samples, which is fewer "
                    f"than cv_folds ({self._cv_folds})."
                ),
            )

        # Step 5: Check if dataset hash matches current active model
        active_meta = self._analyzer.metadata
        if active_meta is None:
            active_meta = self._model_store.load_metadata()

        if active_meta is not None and active_meta.dataset_hash == dataset.dataset_hash:
            return TrainingReport(
                status=TrainingStatus.SKIPPED_UNCHANGED,
                sample_count=sample_count,
                model_version=active_meta.version,
                reason="Dataset hash unchanged since last active model training.",
            )

        # Step 6: Cross-validation quality gating (n_jobs=1 for single core bounding)
        estimator_fn = self._estimator_factory or _default_estimator
        candidate = estimator_fn()
        baseline = DummyClassifier(strategy="most_frequent")
        cv = StratifiedKFold(n_splits=self._cv_folds, shuffle=True, random_state=42)

        x_list = list(features)
        y_list = list(labels)

        candidate_scores = cross_val_score(
            candidate,
            x_list,
            y_list,
            cv=cv,
            scoring="f1_macro",
            n_jobs=1,
        )
        baseline_scores = cross_val_score(
            baseline,
            x_list,
            y_list,
            cv=cv,
            scoring="f1_macro",
            n_jobs=1,
        )

        candidate_f1 = float(sum(candidate_scores) / len(candidate_scores))
        baseline_f1 = float(sum(baseline_scores) / len(baseline_scores))

        current_version = active_meta.version if active_meta is not None else 0

        if candidate_f1 <= baseline_f1 or candidate_f1 < self._min_f1_score:
            return TrainingReport(
                status=TrainingStatus.REJECTED_QUALITY,
                sample_count=sample_count,
                cv_f1_macro=candidate_f1,
                baseline_f1_macro=baseline_f1,
                model_version=current_version if active_meta is not None else None,
                reason=(
                    f"Candidate CV F1 macro ({candidate_f1:.4f}) did not beat baseline "
                    f"({baseline_f1:.4f}) or satisfy min_f1_score ({self._min_f1_score:.4f})."
                ),
            )

        # Step 7: Quality gate passed - train final estimator on full dataset
        final_model = estimator_fn()
        final_model.fit(x_list, y_list)

        new_version = current_version + 1
        metadata = ModelMetadata(
            version=new_version,
            trained_at=datetime.now(timezone.utc),
            analyzer_name=getattr(self._analyzer, "ANALYZER_NAME", "SklearnPedagogicalAnalyzerV1"),
            sample_count=sample_count,
            positive_count=counts.get(1, 0),
            negative_count=counts.get(0, 0),
            cv_f1_macro=candidate_f1,
            baseline_f1_macro=baseline_f1,
            dataset_hash=dataset.dataset_hash,
            feature_names=tuple(dataset.feature_names),
        )

        self._model_store.save(final_model, metadata)
        self._analyzer.update_model(final_model, metadata)

        return TrainingReport(
            status=TrainingStatus.TRAINED,
            sample_count=sample_count,
            cv_f1_macro=candidate_f1,
            baseline_f1_macro=baseline_f1,
            model_version=new_version,
            reason=f"Model v{new_version} trained, validated, and activated.",
        )
