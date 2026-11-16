# Graph Report - Clases  (2026-11-16)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 736 nodes · 2340 edges · 30 communities (17 shown, 13 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 605 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `33583ea6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 28

## God Nodes (most connected - your core abstractions)
1. `Student` - 72 edges
2. `TutoringSession` - 65 edges
3. `AcademicCatalogSnapshot` - 53 edges
4. `Subject` - 49 edges
5. `create_app()` - 49 edges
6. `ExerciseType` - 47 edges
7. `Topic` - 47 edges
8. `AttemptOutcome` - 41 edges
9. `ExerciseAttempt` - 41 edges
10. `ErrorCause` - 39 edges

## Surprising Connections (you probably didn't know these)
- `ExerciseAttemptDTO` --uses--> `AttemptOutcome`  [INFERRED]
  backend/src/tutoring/application/dtos.py → backend/src/tutoring/domain/enums.py
- `ExerciseAttemptDTO` --uses--> `ErrorCause`  [INFERRED]
  backend/src/tutoring/application/dtos.py → backend/src/tutoring/domain/enums.py
- `ExerciseAttemptInputDTO` --uses--> `AttemptOutcome`  [INFERRED]
  backend/src/tutoring/application/dtos.py → backend/src/tutoring/domain/enums.py
- `ExerciseAttemptInputDTO` --uses--> `ErrorCause`  [INFERRED]
  backend/src/tutoring/application/dtos.py → backend/src/tutoring/domain/enums.py
- `ManageCatalogUseCase` --uses--> `ExerciseType`  [INFERRED]
  backend/src/tutoring/application/use_cases/manage_catalog.py → backend/src/tutoring/domain/entities/catalog.py

## Import Cycles
- None detected.

## Communities (30 total, 13 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (45): CatalogTreeDTO, CatalogTreeSubjectDTO, CatalogTreeTopicDTO, CreateExamGoalDTO, CreateExerciseTypeDTO, CreateStudentDTO, CreateSubjectDTO, CreateTopicDTO (+37 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (26): AcademicCatalogSnapshot, ExerciseType, _index_catalog_items(), Subject, Topic, require_non_empty(), SqliteCatalogRepository, test_sklearn_analyzer_fallback_when_untrained() (+18 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (13): InMemoryCatalogRepository, _NamedEntity, ValidationError, test_catalog_api_flow_and_error_handling(), test_session_and_diagnostic_api_endpoints(), test_students_and_exam_goals_api_endpoints(), test_in_memory_catalog_repository(), test_require_non_empty_rejects_blank_text() (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (19): InMemorySessionRepository, TutoringSession, _validate_duration(), AttemptOutcome, ErrorCause, InvalidAttemptError, ExerciseAttempt, SqliteSessionRepository (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (9): InMemoryStudentRepository, Student, init_sqlite_db(), SqliteStudentRepository, test_sqlite_student_persistence_lifecycle(), test_in_memory_student_repository(), test_student_rejects_blank_required_fields(), test_student_upcoming_exams_filters_and_sorts_chronologically() (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (5): GenerateStudentDiagnosticUseCase, PedagogicalAnalyzerPort, CatalogRepository, SessionRepository, StudentRepository

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (43): dependencies, react@^18.3.1, react-dom@^18.3.1, devDependencies, eslint@^9.9.0, @eslint/js@^9.9.0, eslint-plugin-react-hooks@^5.1.0-rc.0, eslint-plugin-react-refresh@^0.4.9 (+35 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (10): ApiError, HttpTutoringApi, CreateExamGoalPayload, CreateExerciseTypePayload, CreateStudentPayload, CreateSubjectPayload, ExamGoal, ExerciseType (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (17): formatDaysRemaining(), riskBadgeClass(), StudentDiagnosticPanel(), StudentDiagnosticPanelProps, trendBadgeClass(), ERROR_CAUSE_LABELS, formatPercent(), OUTCOME_LABELS (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.14
Nodes (10): TutoringApi, CatalogTree, StudentSummary, CatalogPageProps, RecordSessionPageProps, sampleCatalog, StudentDetailPageProps, @testing-library/react (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (6): StudentDiagnosticDTO, ExamAlert, StudentDiagnostic, SubjectPriority, WeakExerciseType, SklearnPedagogicalAnalyzer

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (4): FeatureExtractor, FeatureVector, test_feature_extractor_extracts_student_and_subject_vectors(), test_feature_extractor_handles_empty_student_cleanly()

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (9): _compute_exam_urgency_bonus(), _evaluate_readiness_risk(), compute_dominant_error_cause(), compute_failure_delta(), compute_learning_trend(), TimedAttempt, LearningTrend, test_compute_learning_trend_covers_all_classifications() (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.17
Nodes (7): ActiveSection, App(), AppProps, CatalogPage(), StudentsPage(), StudentsPageProps, react

### Community 16 - "Community 16"
Cohesion: 0.19
Nodes (7): AttemptOutcome, ErrorCause, DraftAttempt, ERROR_CAUSES, formatLocalDateTimeInput(), OUTCOMES, RecordSessionPage()

### Community 17 - "Community 17"
Cohesion: 0.20
Nodes (9): CatalogTreeSubject, CatalogTreeTopic, CreateTopicPayload, ExamAlert, ExerciseAttempt, ExerciseAttemptInput, SubjectPriority, Topic (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `tutoring-app`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 245 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Student` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 10`, `Community 11`, `Community 12`, `Community 15`, `Community 19`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Student` (e.g. with `InMemoryStudentRepository` and `ManageStudentsUseCase`) actually correct?**
  _`Student` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tutoring-app` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05696969696969697 - nodes in this community are weakly interconnected._
- **Why does `TutoringSession` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 10`, `Community 11`, `Community 12`, `Community 15`, `Community 20`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `TutoringSession` (e.g. with `InMemorySessionRepository` and `RecordSessionUseCase`) actually correct?**
  _`TutoringSession` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06610644257703081 - nodes in this community are weakly interconnected._