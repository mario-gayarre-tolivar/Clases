export type AttemptOutcome = 'SUCCESS' | 'PARTIAL' | 'FAILURE';

export type ErrorCause = 'CONCEPT' | 'CALCULATION' | 'COMPREHENSION' | 'CARELESSNESS';

export type LearningTrend =
  | 'IMPROVING'
  | 'STAGNANT'
  | 'REGRESSING'
  | 'INSUFFICIENT_DATA';

export type ReadinessRisk = 'HIGH' | 'MEDIUM' | 'LOW';

export interface ExerciseType {
  id: string;
  topic_id: string;
  name: string;
  description: string;
}

export interface CatalogTreeTopic {
  id: string;
  name: string;
  exercise_types: ExerciseType[];
}

export interface CatalogTreeSubject {
  id: string;
  name: string;
  description: string;
  topics: CatalogTreeTopic[];
}

export interface CatalogTree {
  subjects: CatalogTreeSubject[];
}

export interface Subject {
  id: string;
  name: string;
  description: string;
}

export interface Topic {
  id: string;
  subject_id: string;
  name: string;
}

export interface ExamGoal {
  id: string;
  subject_id: string;
  title: string;
  exam_date: string;
  topic_ids: string[];
}

export interface StudentSummary {
  id: string;
  full_name: string;
  academic_level: string;
}

export interface StudentDetail {
  id: string;
  full_name: string;
  academic_level: string;
  pedagogical_notes: string;
  exam_goals: ExamGoal[];
}

export interface ExerciseAttemptInput {
  exercise_type_id: string;
  outcome: AttemptOutcome;
  error_cause: ErrorCause | null;
  notes: string;
}

export interface ExerciseAttempt {
  exercise_type_id: string;
  outcome: AttemptOutcome;
  error_cause: ErrorCause | null;
  notes: string;
  severity_weight: number;
}

export interface RecordSessionPayload {
  occurred_at: string;
  duration_minutes: number;
  session_notes: string;
  attempts: ExerciseAttemptInput[];
}

export interface SessionRecord {
  id: string;
  student_id: string;
  occurred_at: string;
  duration_minutes: number;
  session_notes: string;
  failure_rate: number;
  attempts: ExerciseAttempt[];
}

export interface SubjectPriority {
  subject_id: string;
  subject_name: string;
  priority_score: number;
  weighted_failure_rate: number;
  upcoming_exam_days: number | null;
  trend: LearningTrend;
  reasons: string[];
}

export interface WeakExerciseType {
  exercise_type_id: string;
  exercise_type_name: string;
  topic_name: string;
  subject_name: string;
  attempts_count: number;
  weighted_failure_rate: number;
  dominant_error_cause: ErrorCause | null;
}

export interface ExamAlert {
  exam_goal_id: string;
  subject_name: string;
  title: string;
  days_remaining: number;
  readiness_risk: ReadinessRisk;
}

export interface StudentDiagnostic {
  student_id: string;
  generated_at: string;
  analyzer_name: string;
  subject_priorities: SubjectPriority[];
  weak_exercise_types: WeakExerciseType[];
  exam_alerts: ExamAlert[];
  overall_trend: LearningTrend;
}

export interface CreateSubjectPayload {
  name: string;
  description?: string;
}

export interface CreateTopicPayload {
  subject_id: string;
  name: string;
}

export interface CreateExerciseTypePayload {
  topic_id: string;
  name: string;
  description?: string;
}

export interface CreateStudentPayload {
  full_name: string;
  academic_level: string;
  pedagogical_notes?: string;
}

export interface CreateExamGoalPayload {
  subject_id: string;
  title: string;
  exam_date: string;
  topic_ids?: string[];
}
