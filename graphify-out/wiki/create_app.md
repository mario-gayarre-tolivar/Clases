# create_app()

> God node · 49 connections · `backend/src/tutoring/presentation/api/app.py`

**Community:** [Community 0](Community_0.md)

## Connections by Relation

### calls
- HeuristicPedagogicalAnalyzer `EXTRACTED`
- ManageCatalogUseCase `EXTRACTED`
- ManageStudentsUseCase `EXTRACTED`
- SqliteCatalogRepository `EXTRACTED`
- RecordSessionUseCase `EXTRACTED`
- SqliteStudentRepository `EXTRACTED`
- SqliteSessionRepository `EXTRACTED`
- GenerateStudentDiagnosticUseCase `EXTRACTED`
- init_sqlite_db() `EXTRACTED`
- CreateTopicDTO `EXTRACTED`
- CreateExerciseTypeDTO `EXTRACTED`
- CreateSubjectDTO `EXTRACTED`
- CreateStudentDTO `EXTRACTED`
- RecordSessionDTO `EXTRACTED`
- CreateExamGoalDTO `EXTRACTED`
- ExerciseAttemptInputDTO `EXTRACTED`
- test_catalog_api_flow_and_error_handling() `EXTRACTED`
- test_session_and_diagnostic_api_endpoints() `EXTRACTED`
- test_students_and_exam_goals_api_endpoints() `EXTRACTED`

### contains
- app.py `EXTRACTED`
- record_session() `EXTRACTED`
- create_subject() `EXTRACTED`
- create_topic() `EXTRACTED`
- create_exercise_type() `EXTRACTED`
- create_student() `EXTRACTED`
- add_exam_goal() `EXTRACTED`
- entity_not_found_handler() `EXTRACTED`
- duplicate_entity_handler() `EXTRACTED`
- validation_error_handler() `EXTRACTED`
- get_catalog() `EXTRACTED`
- list_students() `EXTRACTED`
- get_student() `EXTRACTED`
- list_student_sessions() `EXTRACTED`
- get_student_diagnostic() `EXTRACTED`

### imports
- main.py `EXTRACTED`

### rationale_for
- Instantiate and configure the FastAPI application. `EXTRACTED`

### references
- FastAPI `EXTRACTED`

### uses
- ValidationError `INFERRED`
- EntityNotFoundError `INFERRED`
- DuplicateEntityError `INFERRED`
- StudentDiagnosticDTO `INFERRED`
- StudentDetailDTO `INFERRED`
- SessionDTO `INFERRED`
- ExerciseTypeDTO `INFERRED`
- ExamGoalDTO `INFERRED`
- CatalogTreeDTO `INFERRED`
- SubjectDTO `INFERRED`
- TopicDTO `INFERRED`
- StudentSummaryDTO `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*