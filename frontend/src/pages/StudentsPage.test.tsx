import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { TutoringApi } from '../api/client';
import type { StudentDetail, StudentSummary } from '../domain/types';
import { StudentsPage } from './StudentsPage';

function createMockApi(overrides: Partial<TutoringApi> = {}): TutoringApi {
  return {
    getCatalog: vi.fn(),
    createSubject: vi.fn(),
    createTopic: vi.fn(),
    createExerciseType: vi.fn(),
    listStudents: vi.fn().mockResolvedValue([]),
    createStudent: vi.fn(),
    getStudent: vi.fn(),
    addExamGoal: vi.fn(),
    recordSession: vi.fn(),
    listSessions: vi.fn(),
    getDiagnostic: vi.fn(),
    ...overrides,
  };
}

describe('StudentsPage', () => {
  it('lists students, filters by name, creates a new student, and opens detail', async () => {
    const user = userEvent.setup();
    const onSelectStudent = vi.fn();

    const initialStudents: StudentSummary[] = [
      { id: 'stu-1', full_name: 'Ana López', academic_level: '2º Bachillerato' },
      { id: 'stu-2', full_name: 'Carlos Ruiz', academic_level: '4º ESO' },
    ];
    const createdDetail: StudentDetail = {
      id: 'stu-3',
      full_name: 'Beatriz Vega',
      academic_level: '1º Bachillerato',
      pedagogical_notes: 'Necesita reforzar cálculo',
      exam_goals: [],
    };

    const listStudents = vi
      .fn<TutoringApi['listStudents']>()
      .mockResolvedValueOnce(initialStudents)
      .mockResolvedValueOnce([
        ...initialStudents,
        {
          id: createdDetail.id,
          full_name: createdDetail.full_name,
          academic_level: createdDetail.academic_level,
        },
      ]);

    const createStudent = vi
      .fn<TutoringApi['createStudent']>()
      .mockResolvedValue(createdDetail);

    const api = createMockApi({ listStudents, createStudent });

    render(<StudentsPage api={api} onSelectStudent={onSelectStudent} />);

    expect(await screen.findByText('Ana López')).toBeInTheDocument();
    expect(screen.getByText('Carlos Ruiz')).toBeInTheDocument();

    // Filter by name
    const searchInput = screen.getByLabelText('Buscar alumno');
    await user.type(searchInput, 'Carlos');
    expect(screen.queryByText('Ana López')).not.toBeInTheDocument();
    expect(screen.getByText('Carlos Ruiz')).toBeInTheDocument();

    await user.clear(searchInput);
    expect(screen.getByText('Ana López')).toBeInTheDocument();

    // Create new student inline
    await user.click(screen.getByRole('button', { name: 'Nuevo alumno' }));
    await user.type(screen.getByLabelText('Nombre completo'), 'Beatriz Vega');
    await user.type(screen.getByLabelText('Curso o nivel'), '1º Bachillerato');
    await user.type(
      screen.getByLabelText('Observaciones pedagógicas'),
      'Necesita reforzar cálculo'
    );
    await user.click(screen.getByRole('button', { name: 'Guardar alumno' }));

    await waitFor(() => {
      expect(createStudent).toHaveBeenCalledWith({
        full_name: 'Beatriz Vega',
        academic_level: '1º Bachillerato',
        pedagogical_notes: 'Necesita reforzar cálculo',
      });
    });

    expect(await screen.findByText('Beatriz Vega')).toBeInTheDocument();

    // Open student detail
    await user.click(
      screen.getByRole('button', { name: 'Abrir ficha de Beatriz Vega' })
    );
    expect(onSelectStudent).toHaveBeenCalledWith('stu-3');
  });

  it('shows empty state and error recovery', async () => {
    const user = userEvent.setup();
    const listStudents = vi
      .fn<TutoringApi['listStudents']>()
      .mockRejectedValueOnce(new Error('Servidor no disponible'))
      .mockResolvedValueOnce([]);

    const api = createMockApi({ listStudents });
    render(<StudentsPage api={api} onSelectStudent={vi.fn()} />);

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Servidor no disponible'
    );
    await user.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(
      await screen.findByText('Aún no hay alumnos registrados.')
    ).toBeInTheDocument();
  });
});
