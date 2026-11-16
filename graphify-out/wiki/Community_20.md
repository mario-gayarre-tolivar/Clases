# Community 20

> 6 nodes · cohesion 0.40

## Key Concepts

- **collect_timed_attempts()** (11 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **compute_recency_weight()** (8 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **date** (2 connections)
- **datetime** (2 connections)
- **Compute exponential recency weight w = exp(-lambda * max(0, days_elapsed)).** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **Flatten sessions into chronologically ordered TimedAttempt entries.** (1 connections) — `backend/src/tutoring/domain/analytics/scoring.py`

## Relationships

- [Community 12](Community_12.md) (5 shared connections)
- [Community 11](Community_11.md) (4 shared connections)
- [Community 3](Community_3.md) (3 shared connections)
- [Community 15](Community_15.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/analytics/scoring.py`

## Audit Trail

- EXTRACTED: 18 (95%)
- INFERRED: 1 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*