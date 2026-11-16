# Community 27

> 22 nodes · cohesion 0.23

## Key Concepts

- **EntityNotFoundError** (28 connections) — `backend/src/tutoring/domain/exceptions.py`
- **ManageStudentsUseCase** (22 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **manage_students.py** (21 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **test_add_exam_goal_validates_student_and_subject_existence()** (13 connections) — `backend/tests/unit/application/test_manage_students.py`
- **.add_exam_goal()** (12 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **._to_detail_dto()** (11 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **CreateStudentDTO** (9 connections) — `backend/src/tutoring/application/dtos.py`
- **CreateExamGoalDTO** (8 connections) — `backend/src/tutoring/application/dtos.py`
- **StudentDetailDTO** (8 connections) — `backend/src/tutoring/application/dtos.py`
- **.create_student()** (8 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **.get_student_detail()** (8 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **.get_by_id()** (8 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **test_create_student_and_list_and_get_detail()** (8 connections) — `backend/tests/unit/application/test_manage_students.py`
- **ExamGoalDTO** (7 connections) — `backend/src/tutoring/application/dtos.py`
- **StudentSummaryDTO** (6 connections) — `backend/src/tutoring/application/dtos.py`
- **.list_students()** (4 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **.save()** (4 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **UUID** (3 connections)
- **date** (1 connections)
- **Use cases for managing students and their exam goals.** (1 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **Orchestrates student registrations, profile queries, and exam goal additions.** (1 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **Raised when a referenced domain entity does not exist.** (1 connections) — `backend/src/tutoring/domain/exceptions.py`

## Relationships

- [Community 8](Community_8.md) (19 shared connections)
- [Community 13](Community_13.md) (12 shared connections)
- [Community 4](Community_4.md) (12 shared connections)
- [Community 28](Community_28.md) (9 shared connections)
- [Community 25](Community_25.md) (9 shared connections)
- [Community 24](Community_24.md) (9 shared connections)
- [Community 20](Community_20.md) (8 shared connections)
- [Community 1](Community_1.md) (6 shared connections)
- [Community 17](Community_17.md) (1 shared connections)
- [Community 5](Community_5.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/dtos.py`
- `backend/src/tutoring/application/use_cases/manage_students.py`
- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/domain/ports/repositories.py`
- `backend/tests/unit/application/test_manage_students.py`

## Audit Trail

- EXTRACTED: 84 (60%)
- INFERRED: 55 (40%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*