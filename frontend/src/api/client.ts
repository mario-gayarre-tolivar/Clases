import type {
  CatalogTree,
  CreateExamGoalPayload,
  CreateExerciseTypePayload,
  CreateStudentPayload,
  CreateSubjectPayload,
  CreateTopicPayload,
  ExamGoal,
  ExerciseType,
  RecordSessionPayload,
  SessionRecord,
  StudentDetail,
  StudentDiagnostic,
  StudentSummary,
  Subject,
  Topic,
} from '../domain/types';

export interface TutoringApi {
  getCatalog(): Promise<CatalogTree>;
  createSubject(payload: CreateSubjectPayload): Promise<Subject>;
  createTopic(payload: CreateTopicPayload): Promise<Topic>;
  createExerciseType(payload: CreateExerciseTypePayload): Promise<ExerciseType>;
  listStudents(): Promise<StudentSummary[]>;
  createStudent(payload: CreateStudentPayload): Promise<StudentDetail>;
  getStudent(studentId: string): Promise<StudentDetail>;
  addExamGoal(studentId: string, payload: CreateExamGoalPayload): Promise<ExamGoal>;
  recordSession(studentId: string, payload: RecordSessionPayload): Promise<SessionRecord>;
  listSessions(studentId: string): Promise<SessionRecord[]>;
  getDiagnostic(studentId: string): Promise<StudentDiagnostic>;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export class HttpTutoringApi implements TutoringApi {
  private readonly baseUrl: string;

  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
      ...init,
    });

    if (!response.ok) {
      let detail = `Error HTTP ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: unknown };
        if (typeof body.detail === 'string' && body.detail.trim()) {
          detail = body.detail;
        }
      } catch {
        // Fallback to HTTP status message when error body is not JSON.
      }
      throw new ApiError(response.status, detail);
    }

    return (await response.json()) as T;
  }

  getCatalog(): Promise<CatalogTree> {
    return this.request<CatalogTree>('/api/catalog');
  }

  createSubject(payload: CreateSubjectPayload): Promise<Subject> {
    return this.request<Subject>('/api/catalog/subjects', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  createTopic(payload: CreateTopicPayload): Promise<Topic> {
    return this.request<Topic>('/api/catalog/topics', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  createExerciseType(payload: CreateExerciseTypePayload): Promise<ExerciseType> {
    return this.request<ExerciseType>('/api/catalog/exercise-types', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  listStudents(): Promise<StudentSummary[]> {
    return this.request<StudentSummary[]>('/api/students');
  }

  createStudent(payload: CreateStudentPayload): Promise<StudentDetail> {
    return this.request<StudentDetail>('/api/students', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  getStudent(studentId: string): Promise<StudentDetail> {
    return this.request<StudentDetail>(`/api/students/${studentId}`);
  }

  addExamGoal(studentId: string, payload: CreateExamGoalPayload): Promise<ExamGoal> {
    return this.request<ExamGoal>(`/api/students/${studentId}/exam-goals`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  recordSession(
    studentId: string,
    payload: RecordSessionPayload
  ): Promise<SessionRecord> {
    return this.request<SessionRecord>(`/api/students/${studentId}/sessions`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  listSessions(studentId: string): Promise<SessionRecord[]> {
    return this.request<SessionRecord[]>(`/api/students/${studentId}/sessions`);
  }

  getDiagnostic(studentId: string): Promise<StudentDiagnostic> {
    return this.request<StudentDiagnostic>(`/api/students/${studentId}/diagnostic`);
  }
}
