import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react';

import type { TutoringApi } from '../api/client';
import { ERROR_CAUSE_LABELS, OUTCOME_LABELS, formatPercent } from '../domain/labels';
import type {
  CatalogTree,
  SessionRecord,
  StudentDetail,
  StudentDiagnostic,
} from '../domain/types';
import { StudentDiagnosticPanel } from '../components/StudentDiagnosticPanel';
import { RecordSessionPage } from './RecordSessionPage';

export interface StudentDetailPageProps {
  api: TutoringApi;
  studentId: string;
  onBack: () => void;
  onNavigateToCatalog: () => void;
}

type DetailTab = 'diagnostic' | 'record' | 'history' | 'exams';

export function StudentDetailPage({
  api,
  studentId,
  onBack,
  onNavigateToCatalog,
}: StudentDetailPageProps) {
  const [activeTab, setActiveTab] = useState<DetailTab>('diagnostic');
  const [student, setStudent] = useState<StudentDetail | null>(null);
  const [catalog, setCatalog] = useState<CatalogTree | null>(null);
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [diagnostic, setDiagnostic] = useState<StudentDiagnostic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showExamForm, setShowExamForm] = useState(false);
  const [examSubjectId, setExamSubjectId] = useState('');
  const [examTitle, setExamTitle] = useState('');
  const [examDate, setExamDate] = useState('');
  const [submittingExam, setSubmittingExam] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [stu, cat, sess, diag] = await Promise.all([
        api.getStudent(studentId),
        api.getCatalog(),
        api.listSessions(studentId),
        api.getDiagnostic(studentId),
      ]);
      setStudent(stu);
      setCatalog(cat);
      setSessions(sess);
      setDiagnostic(diag);
      if (cat.subjects.length > 0) {
        setExamSubjectId((prev) => prev || cat.subjects[0].id);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'No se pudo cargar la ficha del alumno.'
      );
    } finally {
      setLoading(false);
    }
  }, [api, studentId]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  const subjectNames = useMemo(() => {
    const map = new Map<string, string>();
    for (const sub of catalog?.subjects ?? []) {
      map.set(sub.id, sub.name);
    }
    return map;
  }, [catalog]);

  const exerciseNames = useMemo(() => {
    const map = new Map<string, { subject: string; topic: string; exercise: string }>();
    for (const sub of catalog?.subjects ?? []) {
      for (const top of sub.topics) {
        for (const ex of top.exercise_types) {
          map.set(ex.id, {
            subject: sub.name,
            topic: top.name,
            exercise: ex.name,
          });
        }
      }
    }
    return map;
  }, [catalog]);

  async function handleAddExam(event: FormEvent) {
    event.preventDefault();
    if (!examSubjectId || !examTitle.trim() || !examDate) return;
    setSubmittingExam(true);
    setError(null);
    try {
      await api.addExamGoal(studentId, {
        subject_id: examSubjectId,
        title: examTitle.trim(),
        exam_date: examDate,
      });
      setExamTitle('');
      setExamDate('');
      setShowExamForm(false);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar el examen.');
    } finally {
      setSubmittingExam(false);
    }
  }

  return (
    <section aria-label="Ficha del alumno">
      <div className="toolbar">
        <button type="button" className="btn btn--ghost" onClick={onBack}>
          Volver a alumnos
        </button>
      </div>

      {error && (
        <div role="alert" className="alert-banner">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn--secondary btn--small"
            onClick={() => void loadAll()}
          >
            Reintentar
          </button>
        </div>
      )}

      {loading && !student && (
        <div className="surface-panel surface-panel--padded" aria-busy="true">
          <div className="skeleton-line" style={{ width: '35%' }} />
          <div className="skeleton-line" style={{ width: '60%' }} />
        </div>
      )}

      {student && (
        <>
          <div className="page-header">
            <div>
              <h1 className="page-title">{student.full_name}</h1>
              <p className="page-subtitle">{student.academic_level}</p>
              {student.pedagogical_notes && (
                <p className="page-subtitle">{student.pedagogical_notes}</p>
              )}
            </div>
          </div>

          <div role="tablist" aria-label="Secciones de la ficha" className="subtabs">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'diagnostic'}
              className="subtab"
              onClick={() => setActiveTab('diagnostic')}
            >
              Diagnóstico
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'record'}
              className="subtab"
              onClick={() => setActiveTab('record')}
            >
              Registrar clase
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'history'}
              className="subtab"
              onClick={() => setActiveTab('history')}
            >
              Historial
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'exams'}
              className="subtab"
              onClick={() => setActiveTab('exams')}
            >
              Exámenes
            </button>
          </div>

          {activeTab === 'diagnostic' && diagnostic && (
            <StudentDiagnosticPanel
              diagnostic={diagnostic}
              onStartRecordSession={() => setActiveTab('record')}
            />
          )}

          {activeTab === 'record' && catalog && (
            <RecordSessionPage
              api={api}
              studentId={student.id}
              catalog={catalog}
              onSessionRecorded={loadAll}
              onNavigateToCatalog={onNavigateToCatalog}
            />
          )}

          {activeTab === 'history' && (
            <div>
              {sessions.length === 0 ? (
                <div className="empty-state">
                  <p className="empty-state__title">Sin clases registradas todavía.</p>
                </div>
              ) : (
                <div className="catalog-list">
                  {sessions.map((session) => (
                    <article key={session.id} className="subject-block">
                      <div className="subject-block__header">
                        <div>
                          <strong className="tabular">
                            {session.occurred_at.slice(0, 10)}
                          </strong>{' '}
                          <span className="page-subtitle tabular">
                            ({session.duration_minutes} min)
                          </span>
                          {session.session_notes && (
                            <p className="page-subtitle">{session.session_notes}</p>
                          )}
                        </div>
                        <span className="badge badge--neutral tabular">
                          Fallo: {formatPercent(session.failure_rate)}
                        </span>
                      </div>

                      {session.attempts.length > 0 && (
                        <ul className="topic-list">
                          {session.attempts.map((attempt, idx) => {
                            const info = exerciseNames.get(attempt.exercise_type_id);
                            return (
                              <li key={`${session.id}-${idx}`} className="topic-item">
                                <div className="topic-item__header">
                                  <span>
                                    <strong>
                                      {info ? info.exercise : attempt.exercise_type_id}
                                    </strong>
                                    {info && (
                                      <span className="page-subtitle">
                                        {' '}
                                        ({info.subject} / {info.topic})
                                      </span>
                                    )}
                                  </span>
                                  <span>
                                    <span
                                      className={`badge ${
                                        attempt.outcome === 'SUCCESS'
                                          ? 'badge--success'
                                          : attempt.outcome === 'PARTIAL'
                                            ? 'badge--warning'
                                            : 'badge--danger'
                                      }`}
                                    >
                                      {OUTCOME_LABELS[attempt.outcome]}
                                    </span>
                                    {attempt.error_cause && (
                                      <span
                                        className="badge badge--neutral"
                                        style={{ marginLeft: '0.5rem' }}
                                      >
                                        {ERROR_CAUSE_LABELS[attempt.error_cause]}
                                      </span>
                                    )}
                                  </span>
                                </div>
                                {attempt.notes && (
                                  <p className="page-subtitle">{attempt.notes}</p>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'exams' && (
            <div>
              <div className="section-header">
                <h2 className="section-title">Objetivos y exámenes</h2>
                {(catalog?.subjects.length ?? 0) > 0 && (
                  <button
                    type="button"
                    className="btn btn--primary btn--small"
                    onClick={() => setShowExamForm((open) => !open)}
                  >
                    {showExamForm ? 'Cancelar' : 'Añadir examen'}
                  </button>
                )}
              </div>

              {showExamForm && (
                <form
                  onSubmit={(e) => void handleAddExam(e)}
                  className="inline-form-panel"
                >
                  <div className="form-grid">
                    <div className="field">
                      <label htmlFor="exam-subject" className="field__label">
                        Asignatura
                      </label>
                      <select
                        id="exam-subject"
                        className="field__select"
                        value={examSubjectId}
                        onChange={(e) => setExamSubjectId(e.target.value)}
                        required
                      >
                        {(catalog?.subjects ?? []).map((sub) => (
                          <option key={sub.id} value={sub.id}>
                            {sub.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="field">
                      <label htmlFor="exam-title" className="field__label">
                        Título del examen
                      </label>
                      <input
                        id="exam-title"
                        type="text"
                        className="field__input"
                        value={examTitle}
                        onChange={(e) => setExamTitle(e.target.value)}
                        required
                      />
                    </div>
                    <div className="field">
                      <label htmlFor="exam-date" className="field__label">
                        Fecha del examen
                      </label>
                      <input
                        id="exam-date"
                        type="date"
                        className="field__input"
                        value={examDate}
                        onChange={(e) => setExamDate(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div className="form-actions">
                    <button
                      type="submit"
                      className="btn btn--primary btn--small"
                      disabled={submittingExam}
                    >
                      Guardar examen
                    </button>
                  </div>
                </form>
              )}

              {student.exam_goals.length === 0 ? (
                <div className="empty-state">
                  <p className="empty-state__title">Sin exámenes registrados.</p>
                  {(catalog?.subjects.length ?? 0) === 0 && (
                    <div className="empty-state__action">
                      <button
                        type="button"
                        className="btn btn--secondary"
                        onClick={onNavigateToCatalog}
                      >
                        Crear asignaturas en catálogo
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="surface-panel table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th scope="col">Título</th>
                        <th scope="col">Asignatura</th>
                        <th scope="col">Fecha</th>
                      </tr>
                    </thead>
                    <tbody>
                      {student.exam_goals.map((goal) => (
                        <tr key={goal.id}>
                          <td>
                            <strong>{goal.title}</strong>
                          </td>
                          <td>
                            {subjectNames.get(goal.subject_id) ?? goal.subject_id}
                          </td>
                          <td className="tabular">{goal.exam_date}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
