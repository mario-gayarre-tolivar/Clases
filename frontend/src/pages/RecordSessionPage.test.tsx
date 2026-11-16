import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { TutoringApi } from '../api/client';
import type { CatalogTree, SessionRecord } from '../domain/types';
import { RecordSessionPage } from './RecordSessionPage';

function createMockApi(overrides: Partial<TutoringApi> = {}): TutoringApi {
  return {
    getCatalog: vi.fn(),
    createSubject: vi.fn(),
    createTopic: vi.fn(),
    createExerciseType: vi.fn(),
    listStudents: vi.fn(),
    createStudent: vi.fn(),
    getStudent: vi.fn(),
    addExamGoal: vi.fn(),
    recordSession: vi.fn(),
    listSessions: vi.fn(),
    getDiagnostic: vi.fn(),
    ...overrides,
  };
}

const sampleCatalog: CatalogTree = {
  subjects: [
    {
      id: 'sub-1',
      name: 'Matemáticas',
      description: '',
      topics: [
        {
          id: 'top-1',
          name: 'Álgebra',
          exercise_types: [
            { id: 'ex-1', topic_id: 'top-1', name: 'Ecuaciones', description: '' },
            { id: 'ex-2', topic_id: 'top-1', name: 'Sistemas', description: '' },
          ],
        },
      ],
    },
  ],
};

describe('RecordSessionPage', () => {
  it('records multiple attempts with conditional error cause and submits clean payload', async () => {
    const user = userEvent.setup();
    const onSessionRecorded = vi.fn();

    const savedSession: SessionRecord = {
      id: 'ses-1',
      student_id: 'stu-1',
      occurred_at: '2026-11-16T18:00:00.000Z',
      duration_minutes: 75,
      session_notes: 'Buen progreso',
      failure_rate: 0.5,
      attempts: [],
    };
    const recordSession = vi
      .fn<TutoringApi['recordSession']>()
      .mockResolvedValue(savedSession);

    const api = createMockApi({ recordSession });

    render(
      <RecordSessionPage
        api={api}
        studentId="stu-1"
        catalog={sampleCatalog}
        onSessionRecorded={onSessionRecorded}
        onNavigateToCatalog={vi.fn()}
      />
    );

    // Duration & session notes
    const durationInput = screen.getByLabelText('Duración (minutos)');
    await user.clear(durationInput);
    await user.type(durationInput, '75');
    await user.type(screen.getByLabelText('Notas de sesión'), 'Buen progreso');

    // Attempt 1 defaults to SUCCESS -> error cause selector must NOT be present
    const attempt1 = screen.getByRole('group', { name: 'Intento 1' });
    expect(within(attempt1).queryByLabelText('Causa del error')).not.toBeInTheDocument();

    // Add second attempt and mark as FAILURE with CONCEPT cause
    await user.click(screen.getByRole('button', { name: 'Añadir ejercicio' }));
    const attempt2 = screen.getByRole('group', { name: 'Intento 2' });
    await user.selectOptions(within(attempt2).getByLabelText('Tipo de ejercicio'), 'ex-2');
    await user.click(within(attempt2).getByRole('button', { name: 'Fallo' }));

    const causeSelect = within(attempt2).getByLabelText('Causa del error');
    await user.selectOptions(causeSelect, 'CONCEPT');
    await user.type(within(attempt2).getByLabelText('Nota del ejercicio'), 'No plantea bien');

    // Verify toggling SUCCESS clears error_cause cleanly
    await user.click(within(attempt2).getByRole('button', { name: 'Acierto' }));
    expect(within(attempt2).queryByLabelText('Causa del error')).not.toBeInTheDocument();
    await user.click(within(attempt2).getByRole('button', { name: 'Fallo' }));
    expect(within(attempt2).getByLabelText('Causa del error')).toHaveValue('');
    await user.selectOptions(within(attempt2).getByLabelText('Causa del error'), 'CONCEPT');

    await user.click(screen.getByRole('button', { name: 'Guardar sesión' }));

    await waitFor(() => {
      expect(recordSession).toHaveBeenCalledTimes(1);
    });

    const [calledStudentId, calledPayload] = recordSession.mock.calls[0];
    expect(calledStudentId).toBe('stu-1');
    expect(calledPayload.duration_minutes).toBe(75);
    expect(calledPayload.session_notes).toBe('Buen progreso');
    expect(calledPayload.attempts).toEqual([
      {
        exercise_type_id: 'ex-1',
        outcome: 'SUCCESS',
        error_cause: null,
        notes: '',
      },
      {
        exercise_type_id: 'ex-2',
        outcome: 'FAILURE',
        error_cause: 'CONCEPT',
        notes: 'No plantea bien',
      },
    ]);
    expect(onSessionRecorded).toHaveBeenCalledTimes(1);
  });

  it('prompts navigating to catalog when no exercise types exist', async () => {
    const user = userEvent.setup();
    const onNavigateToCatalog = vi.fn();

    render(
      <RecordSessionPage
        api={createMockApi()}
        studentId="stu-1"
        catalog={{ subjects: [] }}
        onSessionRecorded={vi.fn()}
        onNavigateToCatalog={onNavigateToCatalog}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Ir al catálogo' }));
    expect(onNavigateToCatalog).toHaveBeenCalledTimes(1);
  });
});
