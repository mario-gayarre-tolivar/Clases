import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react';

import type { TutoringApi } from '../api/client';
import type { StudentSummary } from '../domain/types';

export interface StudentsPageProps {
  api: TutoringApi;
  onSelectStudent: (studentId: string) => void;
}

export function StudentsPage({ api, onSelectStudent }: StudentsPageProps) {
  const [students, setStudents] = useState<StudentSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [fullName, setFullName] = useState('');
  const [academicLevel, setAcademicLevel] = useState('');
  const [pedagogicalNotes, setPedagogicalNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadStudents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const items = await api.listStudents();
      setStudents(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los alumnos.');
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    void loadStudents();
  }, [loadStudents]);

  const filteredStudents = useMemo(() => {
    if (!students) return [];
    const q = searchQuery.trim().toLowerCase();
    if (!q) return students;
    return students.filter(
      (s) =>
        s.full_name.toLowerCase().includes(q) ||
        s.academic_level.toLowerCase().includes(q)
    );
  }, [students, searchQuery]);

  async function handleCreateStudent(event: FormEvent) {
    event.preventDefault();
    if (!fullName.trim() || !academicLevel.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.createStudent({
        full_name: fullName.trim(),
        academic_level: academicLevel.trim(),
        pedagogical_notes: pedagogicalNotes.trim(),
      });
      setFullName('');
      setAcademicLevel('');
      setPedagogicalNotes('');
      setShowCreateForm(false);
      await loadStudents();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo registrar al alumno.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-label="Gestión de alumnos">
      <div className="page-header">
        <div>
          <h1 className="page-title">Alumnos</h1>
        </div>
        <button
          type="button"
          className="btn btn--primary"
          onClick={() => setShowCreateForm((open) => !open)}
        >
          {showCreateForm ? 'Cancelar' : 'Nuevo alumno'}
        </button>
      </div>

      {error && (
        <div role="alert" className="alert-banner">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn--secondary btn--small"
            onClick={() => void loadStudents()}
          >
            Reintentar
          </button>
        </div>
      )}

      {showCreateForm && (
        <form onSubmit={(e) => void handleCreateStudent(e)} className="inline-form-panel">
          <div className="form-grid">
            <div className="field">
              <label htmlFor="student-fullname" className="field__label">
                Nombre completo
              </label>
              <input
                id="student-fullname"
                type="text"
                className="field__input"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="student-level" className="field__label">
                Curso o nivel
              </label>
              <input
                id="student-level"
                type="text"
                className="field__input"
                value={academicLevel}
                onChange={(e) => setAcademicLevel(e.target.value)}
                required
              />
            </div>
            <div className="field field--full">
              <label htmlFor="student-notes" className="field__label">
                Observaciones pedagógicas
              </label>
              <textarea
                id="student-notes"
                className="field__textarea"
                value={pedagogicalNotes}
                onChange={(e) => setPedagogicalNotes(e.target.value)}
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              Guardar alumno
            </button>
          </div>
        </form>
      )}

      {loading && !students && (
        <div className="surface-panel surface-panel--padded" aria-busy="true">
          <div className="skeleton-line" style={{ width: '50%' }} />
          <div className="skeleton-line" style={{ width: '80%' }} />
        </div>
      )}

      {!loading && students && students.length === 0 && (
        <div className="empty-state">
          <p className="empty-state__title">Aún no hay alumnos registrados.</p>
          <div className="empty-state__action">
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => setShowCreateForm(true)}
            >
              Registrar primer alumno
            </button>
          </div>
        </div>
      )}

      {students && students.length > 0 && (
        <>
          <div className="toolbar">
            <div className="field" style={{ minWidth: '240px', maxWidth: '340px', flex: 1 }}>
              <label htmlFor="student-search" className="field__label">
                Buscar alumno
              </label>
              <input
                id="student-search"
                type="search"
                className="field__input"
                placeholder="Filtrar por nombre o curso"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {filteredStudents.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state__title">Ningún alumno coincide con la búsqueda.</p>
            </div>
          ) : (
            <div className="surface-panel table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th scope="col">Nombre</th>
                    <th scope="col">Curso / nivel</th>
                    <th scope="col">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => (
                    <tr key={student.id}>
                      <td>
                        <strong>{student.full_name}</strong>
                      </td>
                      <td>{student.academic_level}</td>
                      <td>
                        <button
                          type="button"
                          className="btn btn--secondary btn--small"
                          aria-label={`Abrir ficha de ${student.full_name}`}
                          onClick={() => onSelectStudent(student.id)}
                        >
                          Abrir ficha
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}
