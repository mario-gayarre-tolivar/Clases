# Community 12

> 19 nodes · cohesion 0.18

## Key Concepts

- **heuristic_analyzer.py** (35 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **scoring.py** (27 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **TimedAttempt** (22 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **LearningTrend** (17 connections) — `backend/src/tutoring/domain/enums.py`
- **compute_learning_trend()** (9 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **compute_dominant_error_cause()** (8 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **test_compute_learning_trend_covers_all_classifications()** (8 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **compute_failure_delta()** (6 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **_ta()** (3 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **_compute_exam_urgency_bonus()** (2 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **_evaluate_readiness_risk()** (2 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **collections** (2 connections)
- **Deterministic heuristic pedagogical analyzer (zero external LLM dependency).** (1 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **Shared deterministic scoring primitives for pedagogical analytics and ML…** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **Return (recent_mean_failure - previous_mean_failure) or None if insufficient.** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **Classify learning evolution by comparing recent vs previous attempt windows.** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **An exercise attempt enriched with its session timestamp and recency weight.** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **Return recency- and severity-weighted dominant error cause, or None.** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **Evolution direction of a student's performance over time.** (1 connections) — `backend/src/tutoring/domain/enums.py`

## Relationships

- [Community 3](Community_3.md) (18 shared connections)
- [Community 15](Community_15.md) (16 shared connections)
- [Community 2](Community_2.md) (16 shared connections)
- [Community 10](Community_10.md) (10 shared connections)
- [Community 11](Community_11.md) (9 shared connections)
- [Community 20](Community_20.md) (5 shared connections)
- [Community 1](Community_1.md) (3 shared connections)
- [Community 5](Community_5.md) (3 shared connections)
- [Community 21](Community_21.md) (2 shared connections)
- [Community 0](Community_0.md) (2 shared connections)
- [Community 4](Community_4.md) (1 shared connections)
- [Community 19](Community_19.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- `backend/src/tutoring/domain/analytics/scoring.py`
- `backend/src/tutoring/domain/enums.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`

## Audit Trail

- EXTRACTED: 97 (83%)
- INFERRED: 20 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*