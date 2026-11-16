import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { TutoringApi } from '../api/client';
import type {
  CatalogTree,
  SessionRecord,
  StudentDetail,
  StudentDiagnostic,
} from '../domain/types';
import { StudentDetailPage } from './StudentDetailPage';

function createMockApi(overrides: Partial<TutoringApi> = {}): TutoringApi {
  return {
    getCatalog: vi.fn().mockResolvedValue({ subjects: [] }),
    createSubject: vi.fn(),
    createTopic: vi.fn(),
    createExerciseType: vi.fn(),
    listStudents: vi.fn(),
    createStudent: vi.fn(),
    getStudent: vi.fn(),
    addExamGoal: vi.fn(),
    recordSession: vi.fn(),
    listSessions: vi.fn().mockResolvedValue([]),
    getDiagnostic: vi.fn(),
    ...overrides,
  };
}

describe('StudentDetailPage', () => {
  it('renders student profile, exam goals tab with inline creation, and session history', async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();

    const catalog: CatalogTree = {
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
                {
                  id: 'ex-1',
                  topic_id: 'top-1',
                  name: 'Ecuaciones',
                  description: '',
                },
              ],
            },
          ],
        },
      ],
    };

    const studentInitial: StudentDetail = {
      id: 'stu-1',
      full_name: 'Elena Navarro',
      academic_level: '2º ESO',
      pedagogical_notes: 'Trabaja bien con ejemplos paso a paso',
      exam_goals: [],
    };

    const studentWithGoal: StudentDetail = {
      ...studentInitial,
      exam_goals: [
        {
          id: 'goal-1',
          subject_id: 'sub-1',
          title: 'Parcial Álgebra',
          exam_date: '2026-11-28',
          topic_ids: [],
        },
      ],
    };

    const sessions: SessionRecord[] = [
      {
        id: 'ses-1',
        student_id: 'stu-1',
        occurred_at: '2026-11-16T17:00:00Z',
        duration_minutes: 60,
        session_notes: 'Repaso general',
        failure_rate: 0.5,
        attempts: [
          {
            exercise_type_id: 'ex-1',
            outcome: 'PARTIAL',
            error_cause: 'CALCULATION',
            notes: 'Error de signo',
            severity_weight: 0.5,
          },
        ],
      },
    ];

    const emptyDiagnostic: StudentDiagnostic = {
      student_id: 'stu-1',
      generated_at: '2026-11-16T00:00:00Z',
      analyzer_name: 'HeuristicPedagogicalAnalyzerV1',
      subject_priorities: [],
      weak_exercise_types: [],
      exam_alerts: [],
      overall_trend: 'INSUFFICIENT_DATA',
    };

    const getStudent = vi
      .fn<TutoringApi['getStudent']>()
      .mockResolvedValueOnce(studentInitial)
      .mockResolvedValueOnce(studentWithGoal);

    const addExamGoal = vi.fn<TutoringApi['addExamGoal']>().mockResolvedValue({
      id: 'goal-1',
      subject_id: 'sub-1',
      title: 'Parcial Álgebra',
      exam_date: '2026-11-28',
      topic_ids: [],
    });

    const api = createMockApi({
      getCatalog: vi.fn().mockResolvedValue(catalog),
      getStudent,
      listSessions: vi.fn().mockResolvedValue(sessions),
      getDiagnostic: vi.fn().mockResolvedValue(emptyDiagnostic),
      addExamGoal,
    });

    render(
      <StudentDetailPage
        api={api}
        studentId="stu-1"
        onBack={onBack}
        onNavigateToCatalog={vi.fn()}
      />
    );

    expect(
      await screen.findByRole('heading', { name: 'Elena Navarro' })
    ).toBeInTheDocument();
    expect(screen.getByText('2º ESO')).toBeInTheDocument();
    expect(
      screen.getByText('Trabaja bien con ejemplos paso a paso')
    ).toBeInTheDocument();

    // Switch to Exámenes tab and add an exam goal
    await user.click(screen.getByRole('tab', { name: 'Exámenes' }));
    await user.click(screen.getByRole('button', { name: 'Añadir examen' }));
    await user.selectOptions(screen.getByLabelText('Asignatura'), 'sub-1');
    await user.type(screen.getByLabelText('Título del examen'), 'Parcial Álgebra');
    await user.type(screen.getByLabelText('Fecha del examen'), '2026-11-28');
    await user.click(screen.getByRole('button', { name: 'Guardar examen' }));

    await waitFor(() => {
      expect(addExamGoal).toHaveBeenCalledWith('stu-1', {
        subject_id: 'sub-1',
        title: 'Parcial Álgebra',
        exam_date: '2026-11-28',
      });
    });

    expect(await screen.findByText('Parcial Álgebra')).toBeInTheDocument();

    // Switch to Historial tab
    await user.click(screen.getByRole('tab', { name: 'Historial' }));
    expect(screen.getByText('Repaso general')).toBeInTheDocument();
    expect(screen.getByText('Ecuaciones')).toBeInTheDocument();
    expect(screen.getByText('Error de signo')).toBeInTheDocument();

    // Back button
    await user.click(screen.getByRole('button', { name: 'Volver a alumnos' }));
    expect(onBack).toHaveBeenCalledTimes(1);
  });
});
