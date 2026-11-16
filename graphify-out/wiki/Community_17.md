# Community 17

> 32 nodes · cohesion 0.10

## Key Concepts

- **catalog.py** (36 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **sklearn_analyzer.py** (21 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **analyzer.py** (16 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **SklearnPedagogicalAnalyzer** (16 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **test_sklearn_analyzer_trained_inference()** (15 connections) — `backend/tests/integration/test_sklearn_analyzer.py`
- **PedagogicalAnalyzerPort** (14 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **test_sklearn_analyzer_fallback_when_untrained()** (14 connections) — `backend/tests/integration/test_sklearn_analyzer.py`
- **StudentDiagnostic** (13 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- **test_sklearn_analyzer.py** (13 connections) — `backend/tests/integration/test_sklearn_analyzer.py`
- **.analyze()** (10 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **.analyze()** (8 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **typing** (5 connections)
- **.__init__()** (4 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **.fit()** (3 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **.is_trained()** (3 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **_NamedEntity** (2 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **Any** (1 connections)
- **Protocol** (1 connections)
- **Taxonomic catalog domain entities and snapshot resolver.** (1 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **date** (1 connections)
- **Protocol** (1 connections)
- **Port contract for pedagogical analysis engines (deterministic or classical ML).** (1 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **Strategy interface decoupled from concrete heuristic or ML implementations.** (1 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **Analyze a student's memory and return explainable diagnostic insights.** (1 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **Complete deterministic or ML-backed diagnostic for a student.** (1 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- *... and 7 more nodes in this community*

## Relationships

- [Community 13](Community_13.md) (26 shared connections)
- [Community 5](Community_5.md) (19 shared connections)
- [Community 2](Community_2.md) (16 shared connections)
- [Community 4](Community_4.md) (14 shared connections)
- [Community 1](Community_1.md) (14 shared connections)
- [Community 12](Community_12.md) (9 shared connections)
- [Community 8](Community_8.md) (9 shared connections)
- [Community 20](Community_20.md) (2 shared connections)
- [Community 27](Community_27.md) (1 shared connections)
- [Community 25](Community_25.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/domain/ports/analyzer.py`
- `backend/src/tutoring/domain/value_objects/diagnostic.py`
- `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- `backend/tests/integration/test_sklearn_analyzer.py`

## Audit Trail

- EXTRACTED: 118 (74%)
- INFERRED: 42 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*