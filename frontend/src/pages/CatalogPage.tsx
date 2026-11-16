import { useCallback, useEffect, useState, type FormEvent } from 'react';

import type { TutoringApi } from '../api/client';
import type { CatalogTree } from '../domain/types';

export interface CatalogPageProps {
  api: TutoringApi;
}

export function CatalogPage({ api }: CatalogPageProps) {
  const [catalog, setCatalog] = useState<CatalogTree | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [showSubjectForm, setShowSubjectForm] = useState(false);
  const [subjectName, setSubjectName] = useState('');
  const [subjectDescription, setSubjectDescription] = useState('');

  const [topicSubjectId, setTopicSubjectId] = useState<string | null>(null);
  const [topicName, setTopicName] = useState('');

  const [exerciseTopicId, setExerciseTopicId] = useState<string | null>(null);
  const [exerciseName, setExerciseName] = useState('');
  const [exerciseDescription, setExerciseDescription] = useState('');

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const tree = await api.getCatalog();
      setCatalog(tree);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar el catálogo.');
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);

  async function handleCreateSubject(event: FormEvent) {
    event.preventDefault();
    if (!subjectName.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.createSubject({
        name: subjectName.trim(),
        description: subjectDescription.trim(),
      });
      setSubjectName('');
      setSubjectDescription('');
      setShowSubjectForm(false);
      await loadCatalog();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear la asignatura.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateTopic(event: FormEvent, subjectId: string) {
    event.preventDefault();
    if (!topicName.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.createTopic({
        subject_id: subjectId,
        name: topicName.trim(),
      });
      setTopicName('');
      setTopicSubjectId(null);
      await loadCatalog();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el tema.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCreateExerciseType(event: FormEvent, topicId: string) {
    event.preventDefault();
    if (!exerciseName.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.createExerciseType({
        topic_id: topicId,
        name: exerciseName.trim(),
        description: exerciseDescription.trim(),
      });
      setExerciseName('');
      setExerciseDescription('');
      setExerciseTopicId(null);
      await loadCatalog();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'No se pudo crear el tipo de ejercicio.'
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-label="Catálogo académico">
      <div className="page-header">
        <div>
          <h1 className="page-title">Catálogo académico</h1>
        </div>
        <button
          type="button"
          className="btn btn--primary"
          onClick={() => setShowSubjectForm((open) => !open)}
        >
          {showSubjectForm ? 'Cancelar' : 'Nueva asignatura'}
        </button>
      </div>

      {error && (
        <div role="alert" className="alert-banner">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn--secondary btn--small"
            onClick={() => void loadCatalog()}
          >
            Reintentar
          </button>
        </div>
      )}

      {showSubjectForm && (
        <form onSubmit={(e) => void handleCreateSubject(e)} className="inline-form-panel">
          <div className="form-grid">
            <div className="field">
              <label htmlFor="subject-name-input" className="field__label">
                Nombre de asignatura
              </label>
              <input
                id="subject-name-input"
                type="text"
                className="field__input"
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="subject-desc-input" className="field__label">
                Descripción (opcional)
              </label>
              <input
                id="subject-desc-input"
                type="text"
                className="field__input"
                value={subjectDescription}
                onChange={(e) => setSubjectDescription(e.target.value)}
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              Guardar asignatura
            </button>
          </div>
        </form>
      )}

      {loading && !catalog && (
        <div className="surface-panel surface-panel--padded" aria-busy="true">
          <div className="skeleton-line" style={{ width: '40%' }} />
          <div className="skeleton-line" style={{ width: '70%' }} />
          <div className="skeleton-line" style={{ width: '55%' }} />
        </div>
      )}

      {!loading && catalog && catalog.subjects.length === 0 && (
        <div className="empty-state">
          <p className="empty-state__title">Aún no hay asignaturas registradas.</p>
          <div className="empty-state__action">
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => setShowSubjectForm(true)}
            >
              Crear primera asignatura
            </button>
          </div>
        </div>
      )}

      {catalog && catalog.subjects.length > 0 && (
        <div className="catalog-list">
          {catalog.subjects.map((subject) => (
            <section
              key={subject.id}
              aria-label={`Asignatura ${subject.name}`}
              className="subject-block"
            >
              <div className="subject-block__header">
                <div>
                  <h2 className="section-title">{subject.name}</h2>
                  {subject.description && (
                    <p className="page-subtitle">{subject.description}</p>
                  )}
                </div>
                <button
                  type="button"
                  className="btn btn--secondary btn--small"
                  onClick={() => {
                    setTopicSubjectId((current) =>
                      current === subject.id ? null : subject.id
                    );
                    setTopicName('');
                  }}
                >
                  Añadir tema
                </button>
              </div>

              {topicSubjectId === subject.id && (
                <form
                  onSubmit={(e) => void handleCreateTopic(e, subject.id)}
                  className="inline-form-panel"
                  style={{ marginTop: '0.75rem', marginBottom: 0 }}
                >
                  <div className="form-grid">
                    <div className="field">
                      <label htmlFor={`topic-name-${subject.id}`} className="field__label">
                        Nombre del tema
                      </label>
                      <input
                        id={`topic-name-${subject.id}`}
                        type="text"
                        className="field__input"
                        value={topicName}
                        onChange={(e) => setTopicName(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div className="form-actions">
                    <button
                      type="submit"
                      className="btn btn--primary btn--small"
                      disabled={submitting}
                    >
                      Guardar tema
                    </button>
                    <button
                      type="button"
                      className="btn btn--ghost btn--small"
                      onClick={() => setTopicSubjectId(null)}
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              )}

              {subject.topics.length === 0 ? (
                <p className="page-subtitle" style={{ marginTop: '0.75rem' }}>
                  Sin temas registrados.
                </p>
              ) : (
                <ul className="topic-list">
                  {subject.topics.map((topic) => (
                    <li
                      key={topic.id}
                      aria-label={`Tema ${topic.name}`}
                      className="topic-item"
                    >
                      <div className="topic-item__header">
                        <strong>{topic.name}</strong>
                        <button
                          type="button"
                          className="btn btn--ghost btn--small"
                          onClick={() => {
                            setExerciseTopicId((current) =>
                              current === topic.id ? null : topic.id
                            );
                            setExerciseName('');
                            setExerciseDescription('');
                          }}
                        >
                          Añadir ejercicio
                        </button>
                      </div>

                      {exerciseTopicId === topic.id && (
                        <form
                          onSubmit={(e) => void handleCreateExerciseType(e, topic.id)}
                          className="inline-form-panel"
                          style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}
                        >
                          <div className="form-grid">
                            <div className="field">
                              <label
                                htmlFor={`exercise-name-${topic.id}`}
                                className="field__label"
                              >
                                Tipo de ejercicio
                              </label>
                              <input
                                id={`exercise-name-${topic.id}`}
                                type="text"
                                className="field__input"
                                value={exerciseName}
                                onChange={(e) => setExerciseName(e.target.value)}
                                required
                              />
                            </div>
                            <div className="field">
                              <label
                                htmlFor={`exercise-desc-${topic.id}`}
                                className="field__label"
                              >
                                Detalle (opcional)
                              </label>
                              <input
                                id={`exercise-desc-${topic.id}`}
                                type="text"
                                className="field__input"
                                value={exerciseDescription}
                                onChange={(e) => setExerciseDescription(e.target.value)}
                              />
                            </div>
                          </div>
                          <div className="form-actions">
                            <button
                              type="submit"
                              className="btn btn--primary btn--small"
                              disabled={submitting}
                            >
                              Guardar ejercicio
                            </button>
                            <button
                              type="button"
                              className="btn btn--ghost btn--small"
                              onClick={() => setExerciseTopicId(null)}
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      )}

                      {topic.exercise_types.length > 0 && (
                        <ul className="exercise-list">
                          {topic.exercise_types.map((ex) => (
                            <li key={ex.id} className="exercise-chip">
                              {ex.name}
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          ))}
        </div>
      )}
    </section>
  );
}
