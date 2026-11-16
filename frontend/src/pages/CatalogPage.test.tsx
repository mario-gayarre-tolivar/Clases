import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { TutoringApi } from '../api/client';
import type { CatalogTree } from '../domain/types';
import { CatalogPage } from './CatalogPage';

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
    listSessions: vi.fn(),
    getDiagnostic: vi.fn(),
    ...overrides,
  };
}

describe('CatalogPage', () => {
  it('displays catalog hierarchy and allows adding subject, topic, and exercise type', async () => {
    const user = userEvent.setup();

    const initialTree: CatalogTree = {
      subjects: [
        {
          id: 'sub-1',
          name: 'Matemáticas',
          description: 'Bachillerato',
          topics: [
            {
              id: 'top-1',
              name: 'Álgebra',
              exercise_types: [
                {
                  id: 'ex-1',
                  topic_id: 'top-1',
                  name: 'Ecuaciones lineales',
                  description: '',
                },
              ],
            },
          ],
        },
      ],
    };

    const updatedTree: CatalogTree = {
      subjects: [
        ...initialTree.subjects,
        {
          id: 'sub-2',
          name: 'Física',
          description: 'Cinemática',
          topics: [
            {
              id: 'top-2',
              name: 'Movimiento rectilíneo',
              exercise_types: [
                {
                  id: 'ex-2',
                  topic_id: 'top-2',
                  name: 'Cálculo de aceleración',
                  description: '',
                },
              ],
            },
          ],
        },
      ],
    };

    const getCatalog = vi
      .fn<TutoringApi['getCatalog']>()
      .mockResolvedValueOnce(initialTree)
      .mockResolvedValueOnce({
        subjects: [
          ...initialTree.subjects,
          {
            id: 'sub-2',
            name: 'Física',
            description: 'Cinemática',
            topics: [],
          },
        ],
      })
      .mockResolvedValueOnce({
        subjects: [
          ...initialTree.subjects,
          {
            id: 'sub-2',
            name: 'Física',
            description: 'Cinemática',
            topics: [{ id: 'top-2', name: 'Movimiento rectilíneo', exercise_types: [] }],
          },
        ],
      })
      .mockResolvedValueOnce(updatedTree);

    const createSubject = vi.fn<TutoringApi['createSubject']>().mockResolvedValue({
      id: 'sub-2',
      name: 'Física',
      description: 'Cinemática',
    });
    const createTopic = vi.fn<TutoringApi['createTopic']>().mockResolvedValue({
      id: 'top-2',
      subject_id: 'sub-2',
      name: 'Movimiento rectilíneo',
    });
    const createExerciseType = vi
      .fn<TutoringApi['createExerciseType']>()
      .mockResolvedValue({
        id: 'ex-2',
        topic_id: 'top-2',
        name: 'Cálculo de aceleración',
        description: '',
      });

    const api = createMockApi({
      getCatalog,
      createSubject,
      createTopic,
      createExerciseType,
    });

    render(<CatalogPage api={api} />);

    expect(await screen.findByText('Matemáticas')).toBeInTheDocument();
    expect(screen.getByText('Álgebra')).toBeInTheDocument();
    expect(screen.getByText('Ecuaciones lineales')).toBeInTheDocument();

    // 1) Create Subject inline
    await user.click(screen.getByRole('button', { name: 'Nueva asignatura' }));
    await user.type(screen.getByLabelText('Nombre de asignatura'), 'Física');
    await user.type(screen.getByLabelText('Descripción (opcional)'), 'Cinemática');
    await user.click(screen.getByRole('button', { name: 'Guardar asignatura' }));

    await waitFor(() => {
      expect(createSubject).toHaveBeenCalledWith({
        name: 'Física',
        description: 'Cinemática',
      });
    });
    expect(await screen.findByText('Física')).toBeInTheDocument();

    // 2) Create Topic under Física
    const physicsSection = screen.getByRole('region', { name: 'Asignatura Física' });
    await user.click(
      within(physicsSection).getByRole('button', { name: 'Añadir tema' })
    );
    await user.type(
      within(physicsSection).getByLabelText('Nombre del tema'),
      'Movimiento rectilíneo'
    );
    await user.click(
      within(physicsSection).getByRole('button', { name: 'Guardar tema' })
    );

    await waitFor(() => {
      expect(createTopic).toHaveBeenCalledWith({
        subject_id: 'sub-2',
        name: 'Movimiento rectilíneo',
      });
    });
    expect(await screen.findByText('Movimiento rectilíneo')).toBeInTheDocument();

    // 3) Create ExerciseType under Movimiento rectilíneo
    const topicBlock = screen.getByRole('listitem', {
      name: 'Tema Movimiento rectilíneo',
    });
    await user.click(
      within(topicBlock).getByRole('button', { name: 'Añadir ejercicio' })
    );
    await user.type(
      within(topicBlock).getByLabelText('Tipo de ejercicio'),
      'Cálculo de aceleración'
    );
    await user.click(
      within(topicBlock).getByRole('button', { name: 'Guardar ejercicio' })
    );

    await waitFor(() => {
      expect(createExerciseType).toHaveBeenCalledWith({
        topic_id: 'top-2',
        name: 'Cálculo de aceleración',
        description: '',
      });
    });
    expect(await screen.findByText('Cálculo de aceleración')).toBeInTheDocument();
  });

  it('shows empty state and error alert with retry when loading fails', async () => {
    const user = userEvent.setup();
    const getCatalog = vi
      .fn<TutoringApi['getCatalog']>()
      .mockRejectedValueOnce(new Error('Fallo de conexión'))
      .mockResolvedValueOnce({ subjects: [] });

    const api = createMockApi({ getCatalog });
    render(<CatalogPage api={api} />);

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Fallo de conexión');

    await user.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(
      await screen.findByText('Aún no hay asignaturas registradas.')
    ).toBeInTheDocument();
  });
});
