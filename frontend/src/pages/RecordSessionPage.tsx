import { useMemo, useState, type FormEvent } from 'react';

import type { TutoringApi } from '../api/client';
import { ERROR_CAUSE_LABELS, OUTCOME_LABELS } from '../domain/labels';
import type { AttemptOutcome, CatalogTree, ErrorCause } from '../domain/types';

export interface RecordSessionPageProps {
  api: TutoringApi;
  studentId: string;
  catalog: CatalogTree;
  onSessionRecorded: () => void | Promise<void>;
  onNavigateToCatalog: () => void;
}

interface DraftAttempt {
  key: number;
  exercise_type_id: string;
  outcome: AttemptOutcome;
  error_cause: ErrorCause | '';
  notes: string;
}

const OUTCOMES: AttemptOutcome[] = ['SUCCESS', 'PARTIAL', 'FAILURE'];
const ERROR_CAUSES: ErrorCause[] = [
  'CONCEPT',
  'CALCULATION',
  'COMPREHENSION',
  'CARELESSNESS',
];

function formatLocalDateTimeInput(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function RecordSessionPage({
  api,
  studentId,
  catalog,
  onSessionRecorded,
  onNavigateToCatalog,
}: RecordSessionPageProps) {
  const groupedExercises = useMemo(() => {
    const groups: {
      label: string;
      items: { id: string; name: string }[];
    }[] = [];
    for (const subject of catalog.subjects) {
      for (const topic of subject.topics) {
        if (topic.exercise_types.length > 0) {
          groups.push({
            label: `${subject.name} / ${topic.name}`,
            items: topic.exercise_types.map((ex) => ({ id: ex.id, name: ex.name })),
          });
        }
      }
    }
    return groups;
  }, [catalog]);

  const firstExerciseId = groupedExercises[0]?.items[0]?.id ?? '';

  const [occurredAt, setOccurredAt] = useState(() =>
    formatLocalDateTimeInput(new Date())
  );
  const [durationMinutes, setDurationMinutes] = useState('60');
  const [sessionNotes, setSessionNotes] = useState('');
  const [nextKey, setNextKey] = useState(2);
  const [attempts, setAttempts] = useState<DraftAttempt[]>(() => [
    {
      key: 1,
      exercise_type_id: firstExerciseId,
      outcome: 'SUCCESS',
      error_cause: '',
      notes: '',
    },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedNotice, setSavedNotice] = useState<string | null>(null);

  if (groupedExercises.length === 0) {
    return (
      <div className="empty-state">
        <p className="empty-state__title">
          Crea al menos un tipo de ejercicio en el catálogo antes de registrar una clase.
        </p>
        <div className="empty-state__action">
          <button
            type="button"
            className="btn btn--primary"
            onClick={onNavigateToCatalog}
          >
            Ir al catálogo
          </button>
        </div>
      </div>
    );
  }

  function updateAttempt(key: number, patch: Partial<DraftAttempt>) {
    setAttempts((rows) =>
      rows.map((row) => (row.key === key ? { ...row, ...patch } : row))
    );
  }

  function handleOutcomeChange(key: number, outcome: AttemptOutcome) {
    setAttempts((rows) =>
      rows.map((row) =>
        row.key === key
          ? {
              ...row,
              outcome,
              error_cause: outcome === 'SUCCESS' ? '' : row.error_cause,
            }
          : row
      )
    );
  }

  function handleAddAttempt() {
    const id = nextKey;
    setNextKey((k) => k + 1);
    setAttempts((rows) => [
      ...rows,
      {
        key: id,
        exercise_type_id: firstExerciseId,
        outcome: 'SUCCESS',
        error_cause: '',
        notes: '',
      },
    ]);
  }

  function handleRemoveAttempt(key: number) {
    setAttempts((rows) => (rows.length > 1 ? rows.filter((r) => r.key !== key) : rows));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const parsedDuration = Number(durationMinutes);
    if (!Number.isFinite(parsedDuration) || parsedDuration <= 0) {
      setError('La duración debe ser mayor que cero.');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSavedNotice(null);

    try {
      await api.recordSession(studentId, {
        occurred_at: new Date(occurredAt).toISOString(),
        duration_minutes: parsedDuration,
        session_notes: sessionNotes.trim(),
        attempts: attempts.map((a) => ({
          exercise_type_id: a.exercise_type_id || firstExerciseId,
          outcome: a.outcome,
          error_cause:
            a.outcome === 'SUCCESS' || a.error_cause === '' ? null : a.error_cause,
          notes: a.notes.trim(),
        })),
      });

      setSessionNotes('');
      setAttempts([
        {
          key: nextKey,
          exercise_type_id: firstExerciseId,
          outcome: 'SUCCESS',
          error_cause: '',
          notes: '',
        },
      ]);
      setNextKey((k) => k + 1);
      setSavedNotice('Sesión registrada.');
      await onSessionRecorded();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo registrar la sesión.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={(e) => void handleSubmit(e)}
      className="surface-panel surface-panel--padded"
    >
      <div className="section-header">
        <h2 className="section-title">Registrar clase</h2>
      </div>

      {error && (
        <div role="alert" className="alert-banner">
          <span>{error}</span>
        </div>
      )}

      {savedNotice && (
        <div role="status" className="notice-banner">
          {savedNotice}
        </div>
      )}

      <div className="form-grid">
        <div className="field">
          <label htmlFor="session-date" className="field__label">
            Fecha y hora
          </label>
          <input
            id="session-date"
            type="datetime-local"
            className="field__input"
            value={occurredAt}
            onChange={(e) => setOccurredAt(e.target.value)}
            required
          />
        </div>

        <div className="field">
          <label htmlFor="session-duration" className="field__label">
            Duración (minutos)
          </label>
          <input
            id="session-duration"
            type="number"
            min={1}
            className="field__input tabular"
            value={durationMinutes}
            onChange={(e) => setDurationMinutes(e.target.value)}
            required
          />
        </div>

        <div className="field field--full">
          <label htmlFor="session-notes" className="field__label">
            Notas de sesión
          </label>
          <textarea
            id="session-notes"
            className="field__textarea"
            value={sessionNotes}
            onChange={(e) => setSessionNotes(e.target.value)}
          />
        </div>
      </div>

      <div className="section-block">
        <div className="section-header">
          <h3 className="section-title">Ejercicios trabajados</h3>
          <button
            type="button"
            className="btn btn--secondary btn--small"
            onClick={handleAddAttempt}
          >
            Añadir ejercicio
          </button>
        </div>

        {attempts.map((attempt, index) => {
          const activeId = attempt.exercise_type_id || firstExerciseId;
          const showCause = attempt.outcome !== 'SUCCESS';

          return (
            <fieldset
              key={attempt.key}
              aria-label={`Intento ${index + 1}`}
              className="attempt-row"
              style={{ borderLeft: 'none', borderRight: 'none', borderTop: 'none', margin: 0 }}
            >
              <div className="field">
                <label
                  htmlFor={`attempt-exercise-${attempt.key}`}
                  className="field__label"
                >
                  Tipo de ejercicio
                </label>
                <select
                  id={`attempt-exercise-${attempt.key}`}
                  className="field__select"
                  value={activeId}
                  onChange={(e) =>
                    updateAttempt(attempt.key, { exercise_type_id: e.target.value })
                  }
                >
                  {groupedExercises.map((group) => (
                    <optgroup key={group.label} label={group.label}>
                      {group.items.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>

              <div className="field">
                <span className="field__label">Resultado</span>
                <div className="segmented" role="group" aria-label="Resultado">
                  {OUTCOMES.map((outcome) => (
                    <button
                      key={outcome}
                      type="button"
                      className="segmented__btn"
                      data-outcome={outcome}
                      aria-pressed={attempt.outcome === outcome}
                      onClick={() => handleOutcomeChange(attempt.key, outcome)}
                    >
                      {OUTCOME_LABELS[outcome]}
                    </button>
                  ))}
                </div>
              </div>

              {showCause && (
                <div className="field">
                  <label
                    htmlFor={`attempt-cause-${attempt.key}`}
                    className="field__label"
                  >
                    Causa del error
                  </label>
                  <select
                    id={`attempt-cause-${attempt.key}`}
                    className="field__select"
                    value={attempt.error_cause}
                    onChange={(e) =>
                      updateAttempt(attempt.key, {
                        error_cause: e.target.value as ErrorCause | '',
                      })
                    }
                  >
                    <option value="">Sin especificar</option>
                    {ERROR_CAUSES.map((cause) => (
                      <option key={cause} value={cause}>
                        {ERROR_CAUSE_LABELS[cause]}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="field">
                <label
                  htmlFor={`attempt-note-${attempt.key}`}
                  className="field__label"
                >
                  Nota del ejercicio
                </label>
                <input
                  id={`attempt-note-${attempt.key}`}
                  type="text"
                  className="field__input"
                  value={attempt.notes}
                  onChange={(e) =>
                    updateAttempt(attempt.key, { notes: e.target.value })
                  }
                />
              </div>

              {attempts.length > 1 && (
                <button
                  type="button"
                  className="btn btn--ghost btn--small"
                  aria-label={`Quitar intento ${index + 1}`}
                  onClick={() => handleRemoveAttempt(attempt.key)}
                >
                  Quitar
                </button>
              )}
            </fieldset>
          );
        })}
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          Guardar sesión
        </button>
      </div>
    </form>
  );
}
