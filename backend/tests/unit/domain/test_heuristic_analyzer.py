"""Unit tests for HeuristicPedagogicalAnalyzer (T2.1 - T2.5)."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from tutoring.domain.analytics.heuristic_analyzer import HeuristicPedagogicalAnalyzer
from tutoring.domain.analytics.scoring import (
    TimedAttempt,
    compute_dominant_error_cause,
    compute_learning_trend,
    compute_recency_weight,
    compute_weighted_failure_rate,
)
from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause, LearningTrend
from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.exam_goal import ExamGoal


def test_analyzer_rejects_invalid_hyperparameters() -> None:
    with pytest.raises(ValidationError):
        HeuristicPedagogicalAnalyzer(decay_lambda=-0.01)
    with pytest.raises(ValidationError):
        HeuristicPedagogicalAnalyzer(exam_horizon_days=-1)
    with pytest.raises(ValidationError):
        HeuristicPedagogicalAnalyzer(trend_threshold=-0.1)
    with pytest.raises(ValidationError):
        HeuristicPedagogicalAnalyzer(min_trend_attempts=1)


def test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(
        subjects=[math],
        topics=[topic],
        exercise_types=[ex_type],
    )
    student = Student(id=uuid4(), full_name="Sofía", academic_level="4º ESO")
    analyzer = HeuristicPedagogicalAnalyzer()

    diagnostic = analyzer.analyze(
        student=student,
        sessions=[],
        catalog=catalog,
        reference_date=date(2026, 11, 16),
    )

    assert diagnostic.student_id == student.id
    assert diagnostic.analyzer_name == "HeuristicPedagogicalAnalyzerV1"
    assert diagnostic.generated_at == datetime(2026, 11, 16, 0, 0, tzinfo=timezone.utc)
    assert diagnostic.subject_priorities == ()
    assert diagnostic.weak_exercise_types == ()
    assert diagnostic.exam_alerts == ()
    assert diagnostic.overall_trend == LearningTrend.INSUFFICIENT_DATA


def test_recency_weight_and_weighted_failure_rate_prioritize_recent_errors() -> None:
    ref_date = date(2026, 11, 16)
    ex_id = uuid4()
    old_dt = datetime(2026, 10, 17, 17, 0, tzinfo=timezone.utc)  # 30 days ago
    today_dt = datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc)  # 0 days ago

    w_today = compute_recency_weight(today_dt, ref_date, decay_lambda=0.05)
    w_old = compute_recency_weight(old_dt, ref_date, decay_lambda=0.05)
    assert w_today == pytest.approx(1.0)
    assert w_old == pytest.approx(0.22313, rel=1e-3)
    assert w_today > w_old

    # Scenario A: recent failure + old success -> high weighted failure rate (> 0.5)
    recent_fail_rate = compute_weighted_failure_rate(
        [
            TimedAttempt(
                old_dt,
                ExerciseAttempt(ex_id, AttemptOutcome.SUCCESS),
                w_old,
            ),
            TimedAttempt(
                today_dt,
                ExerciseAttempt(ex_id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
                w_today,
            ),
        ]
    )
    # Scenario B: old failure + recent success -> low weighted failure rate (< 0.5)
    old_fail_rate = compute_weighted_failure_rate(
        [
            TimedAttempt(
                old_dt,
                ExerciseAttempt(ex_id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
                w_old,
            ),
            TimedAttempt(
                today_dt,
                ExerciseAttempt(ex_id, AttemptOutcome.SUCCESS),
                w_today,
            ),
        ]
    )

    assert recent_fail_rate > 0.8
    assert old_fail_rate < 0.2
    assert recent_fail_rate > old_fail_rate


def test_analyzer_subject_weighted_failure_rate_reflects_recency() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(
        subjects=[math], topics=[topic], exercise_types=[ex_type]
    )
    student = Student(id=uuid4(), full_name="Sofía", academic_level="4º ESO")

    old_session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 10, 17, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex_type.id, AttemptOutcome.SUCCESS)],
    )
    today_session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_type.id, AttemptOutcome.FAILURE, ErrorCause.CALCULATION)
        ],
    )

    diagnostic = HeuristicPedagogicalAnalyzer(decay_lambda=0.05).analyze(
        student=student,
        sessions=[old_session, today_session],
        catalog=catalog,
        reference_date=ref_date,
    )

    assert len(diagnostic.subject_priorities) == 1
    assert diagnostic.subject_priorities[0].weighted_failure_rate > 0.8


def test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    algebra = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    optics = Topic(id=uuid4(), subject_id=physics.id, name="Óptica")
    ex_math = ExerciseType(id=uuid4(), topic_id=algebra.id, name="Sistemas")
    ex_physics = ExerciseType(id=uuid4(), topic_id=optics.id, name="Lentes")
    catalog = AcademicCatalogSnapshot(
        subjects=[math, physics],
        topics=[algebra, optics],
        exercise_types=[ex_math, ex_physics],
    )

    # Physics has slightly lower failure rate (0.5 vs 0.6) OR equal failure rate (0.5 vs 0.5)
    # but has an exam in 3 days -> must rank first!
    exam_physics = ExamGoal(
        id=uuid4(),
        subject_id=physics.id,
        title="Parcial Óptica",
        exam_date=date(2026, 11, 19),
    )
    student = Student(
        id=uuid4(),
        full_name="Carlos",
        academic_level="2º Bachillerato",
        exam_goals=[exam_physics],
    )
    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.PARTIAL, ErrorCause.CALCULATION),
            ExerciseAttempt(ex_physics.id, AttemptOutcome.PARTIAL, ErrorCause.CONCEPT),
        ],
    )

    diagnostic = HeuristicPedagogicalAnalyzer().analyze(
        student=student,
        sessions=[session],
        catalog=catalog,
        reference_date=ref_date,
    )

    assert [p.subject_name for p in diagnostic.subject_priorities] == [
        "Física",
        "Matemáticas",
    ]
    top = diagnostic.subject_priorities[0]
    second = diagnostic.subject_priorities[1]
    assert top.priority_score > second.priority_score
    assert top.upcoming_exam_days == 3
    assert second.upcoming_exam_days is None
    assert any("Examen próximo en 3 días" in reason for reason in top.reasons)
    assert any("Tasa ponderada de fallo" in reason for reason in top.reasons)


def test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    chem = Subject(id=uuid4(), name="Química")
    t_math = Topic(id=uuid4(), subject_id=math.id, name="Cálculo")
    t_phy = Topic(id=uuid4(), subject_id=physics.id, name="Dinámica")
    t_chem = Topic(id=uuid4(), subject_id=chem.id, name="Enlace")
    ex_math = ExerciseType(id=uuid4(), topic_id=t_math.id, name="Integrales")
    ex_phy = ExerciseType(id=uuid4(), topic_id=t_phy.id, name="Fuerzas")
    ex_chem = ExerciseType(id=uuid4(), topic_id=t_chem.id, name="Lewis")
    catalog = AcademicCatalogSnapshot(
        subjects=[math, physics, chem],
        topics=[t_math, t_phy, t_chem],
        exercise_types=[ex_math, ex_phy, ex_chem],
    )

    exam_high_unpracticed = ExamGoal(
        id=uuid4(),
        subject_id=chem.id,
        title="Control Enlace",
        exam_date=date(2026, 11, 20),  # 4 days, 0 practice -> HIGH
    )
    exam_medium = ExamGoal(
        id=uuid4(),
        subject_id=physics.id,
        title="Control Dinámica",
        exam_date=date(2026, 11, 21),  # 5 days, 0% failure -> MEDIUM (<= 7 days)
    )
    exam_low = ExamGoal(
        id=uuid4(),
        subject_id=math.id,
        title="Global Cálculo",
        exam_date=date(2026, 11, 28),  # 12 days, 0% failure -> LOW
    )
    student = Student(
        id=uuid4(),
        full_name="Elena",
        academic_level="1º Bachillerato",
        exam_goals=[exam_low, exam_high_unpracticed, exam_medium],
    )
    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.SUCCESS),
        ],
    )

    diagnostic = HeuristicPedagogicalAnalyzer().analyze(
        student=student,
        sessions=[session],
        catalog=catalog,
        reference_date=ref_date,
    )

    assert [a.title for a in diagnostic.exam_alerts] == [
        "Control Enlace",
        "Control Dinámica",
        "Global Cálculo",
    ]
    assert [a.readiness_risk for a in diagnostic.exam_alerts] == [
        "HIGH",
        "MEDIUM",
        "LOW",
    ]
    chem_priority = next(
        p for p in diagnostic.subject_priorities if p.subject_id == chem.id
    )
    assert chem_priority.weighted_failure_rate == 0.0
    assert chem_priority.upcoming_exam_days == 4
    assert any("Sin práctica registrada" in r for r in chem_priority.reasons)


def test_dominant_error_cause_uses_recency_and_severity_weights() -> None:
    ref_date = date(2026, 11, 16)
    ex_id = uuid4()
    old_dt = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)
    today_dt = datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc)
    w_old = compute_recency_weight(old_dt, ref_date, decay_lambda=0.05)
    w_today = compute_recency_weight(today_dt, ref_date, decay_lambda=0.05)

    attempts = [
        TimedAttempt(
            old_dt,
            ExerciseAttempt(ex_id, AttemptOutcome.FAILURE, ErrorCause.CARELESSNESS),
            w_old,
        ),
        TimedAttempt(
            old_dt,
            ExerciseAttempt(ex_id, AttemptOutcome.FAILURE, ErrorCause.CARELESSNESS),
            w_old,
        ),
        TimedAttempt(
            today_dt,
            ExerciseAttempt(ex_id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
            w_today,
        ),
    ]

    assert compute_dominant_error_cause(attempts) == ErrorCause.CONCEPT
    assert (
        compute_dominant_error_cause(
            [
                TimedAttempt(
                    today_dt, ExerciseAttempt(ex_id, AttemptOutcome.SUCCESS), w_today
                )
            ]
        )
        is None
    )


def test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    algebra = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    calculus = Topic(id=uuid4(), subject_id=math.id, name="Cálculo")
    ex_mastered = ExerciseType(id=uuid4(), topic_id=algebra.id, name="Ecuación 1er grado")
    ex_partial = ExerciseType(id=uuid4(), topic_id=algebra.id, name="Sistemas lineales")
    ex_hard = ExerciseType(id=uuid4(), topic_id=calculus.id, name="Integrales por partes")
    catalog = AcademicCatalogSnapshot(
        subjects=[math],
        topics=[algebra, calculus],
        exercise_types=[ex_mastered, ex_partial, ex_hard],
    )
    student = Student(id=uuid4(), full_name="Hugo", academic_level="2º Bach")

    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_mastered.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(
                ex_partial.id, AttemptOutcome.PARTIAL, ErrorCause.CALCULATION
            ),
            ExerciseAttempt(
                ex_hard.id, AttemptOutcome.FAILURE, ErrorCause.COMPREHENSION
            ),
        ],
    )

    diagnostic = HeuristicPedagogicalAnalyzer().analyze(
        student=student,
        sessions=[session],
        catalog=catalog,
        reference_date=ref_date,
    )

    assert [w.exercise_type_name for w in diagnostic.weak_exercise_types] == [
        "Integrales por partes",
        "Sistemas lineales",
    ]
    hard = diagnostic.weak_exercise_types[0]
    assert hard.subject_name == "Matemáticas"
    assert hard.topic_name == "Cálculo"
    assert hard.attempts_count == 1
    assert hard.weighted_failure_rate == pytest.approx(1.0)
    assert hard.dominant_error_cause == ErrorCause.COMPREHENSION


def test_compute_learning_trend_covers_all_classifications() -> None:
    ex_id = uuid4()
    t1 = datetime(2026, 11, 1, 17, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 11, 5, 17, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 11, 10, 17, 0, tzinfo=timezone.utc)
    t4 = datetime(2026, 11, 15, 17, 0, tzinfo=timezone.utc)

    def _ta(dt: datetime, outcome: AttemptOutcome) -> TimedAttempt:
        cause = ErrorCause.CONCEPT if outcome != AttemptOutcome.SUCCESS else None
        return TimedAttempt(dt, ExerciseAttempt(ex_id, outcome, cause), 1.0)

    # Fewer than 4 attempts -> INSUFFICIENT_DATA
    assert (
        compute_learning_trend(
            [_ta(t1, AttemptOutcome.FAILURE), _ta(t2, AttemptOutcome.SUCCESS)]
        )
        == LearningTrend.INSUFFICIENT_DATA
    )

    # Earlier failures -> later successes => IMPROVING
    assert (
        compute_learning_trend(
            [
                _ta(t1, AttemptOutcome.FAILURE),
                _ta(t2, AttemptOutcome.FAILURE),
                _ta(t3, AttemptOutcome.SUCCESS),
                _ta(t4, AttemptOutcome.SUCCESS),
            ]
        )
        == LearningTrend.IMPROVING
    )

    # Earlier successes -> later failures => REGRESSING
    assert (
        compute_learning_trend(
            [
                _ta(t1, AttemptOutcome.SUCCESS),
                _ta(t2, AttemptOutcome.SUCCESS),
                _ta(t3, AttemptOutcome.FAILURE),
                _ta(t4, AttemptOutcome.FAILURE),
            ]
        )
        == LearningTrend.REGRESSING
    )

    # Steady partial performance => STAGNANT
    assert (
        compute_learning_trend(
            [
                _ta(t1, AttemptOutcome.PARTIAL),
                _ta(t2, AttemptOutcome.PARTIAL),
                _ta(t3, AttemptOutcome.PARTIAL),
                _ta(t4, AttemptOutcome.PARTIAL),
            ]
        )
        == LearningTrend.STAGNANT
    )


def test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() -> None:
    ref_date = date(2026, 11, 16)
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    t_math = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    t_phy = Topic(id=uuid4(), subject_id=physics.id, name="Cinemática")
    ex_math = ExerciseType(id=uuid4(), topic_id=t_math.id, name="Polinomios")
    ex_phy = ExerciseType(id=uuid4(), topic_id=t_phy.id, name="MRUA")
    catalog = AcademicCatalogSnapshot(
        subjects=[math, physics],
        topics=[t_math, t_phy],
        exercise_types=[ex_math, ex_phy],
    )
    student = Student(id=uuid4(), full_name="Lucía", academic_level="4º ESO")

    # Math regresses (success -> failure), Physics improves (failure -> success)
    s1 = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 2, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(ex_math.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT),
        ],
    )
    s2 = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[
            ExerciseAttempt(ex_math.id, AttemptOutcome.FAILURE, ErrorCause.CALCULATION),
            ExerciseAttempt(ex_math.id, AttemptOutcome.FAILURE, ErrorCause.CALCULATION),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.SUCCESS),
            ExerciseAttempt(ex_phy.id, AttemptOutcome.SUCCESS),
        ],
    )

    diagnostic = HeuristicPedagogicalAnalyzer().analyze(
        student=student,
        sessions=[s1, s2],
        catalog=catalog,
        reference_date=ref_date,
    )

    by_name = {p.subject_name: p for p in diagnostic.subject_priorities}
    assert by_name["Matemáticas"].trend == LearningTrend.REGRESSING
    assert any("regresión" in r.lower() for r in by_name["Matemáticas"].reasons)
    assert by_name["Física"].trend == LearningTrend.IMPROVING
    assert any("mejora" in r.lower() for r in by_name["Física"].reasons)
    # Combined attempts went 2/4 fail -> 2/4 fail => overall STAGNANT
    assert diagnostic.overall_trend == LearningTrend.STAGNANT
