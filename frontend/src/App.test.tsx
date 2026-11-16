import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { TutoringApi } from './api/client';
import { App } from './App';

function createMockApi(): TutoringApi {
  return {
    getCatalog: vi.fn().mockResolvedValue({ subjects: [] }),
    createSubject: vi.fn(),
    createTopic: vi.fn(),
    createExerciseType: vi.fn(),
    listStudents: vi.fn().mockResolvedValue([
      { id: 'stu-1', full_name: 'Mateo Díaz', academic_level: '3º ESO' },
    ]),
    createStudent: vi.fn(),
    getStudent: vi.fn().mockResolvedValue({
      id: 'stu-1',
      full_name: 'Mateo Díaz',
      academic_level: '3º ESO',
      pedagogical_notes: '',
      exam_goals: [],
    }),
    addExamGoal: vi.fn(),
    recordSession: vi.fn(),
    listSessions: vi.fn().mockResolvedValue([]),
    getDiagnostic: vi.fn().mockResolvedValue({
      student_id: 'stu-1',
      generated_at: '2026-11-16T00:00:00Z',
      analyzer_name: 'HeuristicPedagogicalAnalyzerV1',
      overall_trend: 'INSUFFICIENT_DATA',
      exam_alerts: [],
      subject_priorities: [],
      weak_exercise_types: [],
    }),
  };
}

describe('App navigation', () => {
  it('navigates between students list, student detail, and academic catalog', async () => {
    const user = userEvent.setup();
    const api = createMockApi();

    render(<App api={api} />);

    // Starts on Students view
    expect(await screen.findByText('Mateo Díaz')).toBeInTheDocument();

    // Switch to Catalog view via top nav
    await user.click(screen.getByRole('button', { name: 'Catálogo' }));
    expect(
      await screen.findByRole('heading', { name: 'Catálogo académico' })
    ).toBeInTheDocument();

    // Back to Students and open student detail
    await user.click(screen.getByRole('button', { name: 'Alumnos' }));
    await user.click(
      await screen.findByRole('button', { name: 'Abrir ficha de Mateo Díaz' })
    );
    expect(
      await screen.findByRole('heading', { name: 'Mateo Díaz' })
    ).toBeInTheDocument();
  });
});
