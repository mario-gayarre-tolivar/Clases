# Student

> God node · 72 connections · `backend/src/tutoring/domain/entities/student.py`

**Community:** [Community 4](Community_4.md)

## Connections by Relation

### calls
- .create_student() `EXTRACTED`

### contains
- student.py `EXTRACTED`

### imports
- heuristic_analyzer.py `EXTRACTED`
- feature_extractor.py `EXTRACTED`
- repositories.py `EXTRACTED`
- fakes.py `EXTRACTED`
- manage_students.py `EXTRACTED`
- sklearn_analyzer.py `EXTRACTED`
- analyzer.py `EXTRACTED`
- sqlite_student_repo.py `EXTRACTED`
- entities/__init__.py `EXTRACTED`

### method
- .id() `EXTRACTED`
- .upcoming_exams() `EXTRACTED`
- .add_exam_goal() `EXTRACTED`
- .exam_goals() `EXTRACTED`
- .rename() `EXTRACTED`
- .__init__() `EXTRACTED`
- .update_academic_level() `EXTRACTED`
- ._append_unique_exam_goal() `EXTRACTED`
- .full_name() `EXTRACTED`
- .academic_level() `EXTRACTED`
- .pedagogical_notes() `EXTRACTED`
- .update_pedagogical_notes() `EXTRACTED`
- .__repr__() `EXTRACTED`
- .__eq__() `EXTRACTED`

### rationale_for
- Aggregate root holding a student's profile, pedagogical notes, and exam goals. `EXTRACTED`

### references
- .analyze() `EXTRACTED`
- .extract_subject_features() `EXTRACTED`
- ._to_detail_dto() `EXTRACTED`
- .extract_student_features() `EXTRACTED`
- .analyze() `EXTRACTED`
- .save() `EXTRACTED`
- .analyze() `EXTRACTED`
- .get_by_id() `EXTRACTED`
- .save() `EXTRACTED`
- ._hydrate_student() `EXTRACTED`
- .get_by_id() `EXTRACTED`
- .list_all() `EXTRACTED`
- .save() `EXTRACTED`
- .get_by_id() `EXTRACTED`
- .list_all() `EXTRACTED`
- .list_all() `EXTRACTED`

### uses
- ExamGoal `INFERRED`
- HeuristicPedagogicalAnalyzer `INFERRED`
- ValidationError `INFERRED`
- test_generate_student_diagnostic_orchestration() `INFERRED`
- test_sqlite_session_persistence_lifecycle() `INFERRED`
- ManageStudentsUseCase `INFERRED`
- StudentRepository `INFERRED`
- test_record_session_validates_student_and_exercise_types_and_saves() `INFERRED`
- FeatureExtractor `INFERRED`
- DuplicateEntityError `INFERRED`
- SklearnPedagogicalAnalyzer `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- SqliteStudentRepository `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- InMemoryStudentRepository `INFERRED`
- PedagogicalAnalyzerPort `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_sqlite_student_persistence_lifecycle() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- *…and 10 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*