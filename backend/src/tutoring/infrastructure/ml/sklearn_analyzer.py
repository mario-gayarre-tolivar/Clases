"""Machine learning adapter implementing PedagogicalAnalyzerPort using scikit-learn."""

from collections.abc import Sequence
from datetime import date
from typing import Any

from tutoring.domain.analytics.feature_extractor import FeatureExtractor
from tutoring.domain.analytics.heuristic_analyzer import HeuristicPedagogicalAnalyzer
from tutoring.domain.entities.catalog import AcademicCatalogSnapshot
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.ports.analyzer import PedagogicalAnalyzerPort
from tutoring.domain.value_objects.diagnostic import StudentDiagnostic, SubjectPriority


class SklearnPedagogicalAnalyzer(PedagogicalAnalyzerPort):
    """Classical ML adapter using scikit-learn with safe fallback to heuristic analysis."""

    ANALYZER_NAME = "SklearnPedagogicalAnalyzerV1"

    def __init__(
        self,
        classifier: Any | None = None,
        feature_extractor: FeatureExtractor | None = None,
        fallback_analyzer: HeuristicPedagogicalAnalyzer | None = None,
    ) -> None:
        self._classifier = classifier
        self._feature_extractor = feature_extractor or FeatureExtractor()
        self._fallback_analyzer = fallback_analyzer or HeuristicPedagogicalAnalyzer()
        self._is_trained = False

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def fit(self, x: Sequence[Sequence[float]], y: Sequence[int]) -> None:
        """Train the underlying classical classifier on tabular feature vectors."""
        if self._classifier is not None:
            self._classifier.fit(list(x), list(y))
            self._is_trained = True

    def analyze(
        self,
        student: Student,
        sessions: Sequence[TutoringSession],
        catalog: AcademicCatalogSnapshot,
        reference_date: date,
    ) -> StudentDiagnostic:
        """Produce diagnostic using classical ML model or safe heuristic fallback."""
        base_diagnostic = self._fallback_analyzer.analyze(
            student=student,
            sessions=sessions,
            catalog=catalog,
            reference_date=reference_date,
        )

        if not self._is_trained or self._classifier is None:
            return base_diagnostic

        ml_priorities: list[SubjectPriority] = []
        for p in base_diagnostic.subject_priorities:
            feat_vec = self._feature_extractor.extract_subject_features(
                student=student,
                subject_id=p.subject_id,
                sessions=sessions,
                catalog=catalog,
                reference_date=reference_date,
            )
            # Predict urgency / priority class (1 = High focus, 0 = Normal)
            prediction = self._classifier.predict([list(feat_vec.values)])[0]
            ml_bonus = 20.0 if prediction == 1 else 0.0
            adjusted_score = round(min(100.0, p.priority_score + ml_bonus), 2)
            ml_reason = (
                "Modelo ML clásico (Scikit-Learn): Clasificado como prioridad ALTA"
                if prediction == 1
                else "Modelo ML clásico (Scikit-Learn): Clasificado como prioridad NORMAL"
            )
            ml_priorities.append(
                SubjectPriority(
                    subject_id=p.subject_id,
                    subject_name=p.subject_name,
                    priority_score=adjusted_score,
                    weighted_failure_rate=p.weighted_failure_rate,
                    upcoming_exam_days=p.upcoming_exam_days,
                    trend=p.trend,
                    reasons=(*p.reasons, ml_reason),
                )
            )

        ml_priorities.sort(
            key=lambda item: (-item.priority_score, -item.weighted_failure_rate, item.subject_name)
        )

        return StudentDiagnostic(
            student_id=base_diagnostic.student_id,
            generated_at=base_diagnostic.generated_at,
            analyzer_name=self.ANALYZER_NAME,
            subject_priorities=tuple(ml_priorities),
            weak_exercise_types=base_diagnostic.weak_exercise_types,
            exam_alerts=base_diagnostic.exam_alerts,
            overall_trend=base_diagnostic.overall_trend,
        )
