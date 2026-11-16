import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import type { StudentDiagnostic } from '../domain/types';
import { StudentDiagnosticPanel } from './StudentDiagnosticPanel';

describe('StudentDiagnosticPanel', () => {
  it('renders exam alerts, subject priority ranking with reasons, and weak exercise types', () => {
    const diagnostic: StudentDiagnostic = {
      student_id: 'stu-1',
      generated_at: '2026-11-16T00:00:00Z',
      analyzer_name: 'HeuristicPedagogicalAnalyzerV1',
      overall_trend: 'REGRESSING',
      exam_alerts: [
        {
          exam_goal_id: 'goal-1',
          subject_name: 'Física',
          title: 'Parcial Dinámica',
          days_remaining: 3,
          readiness_risk: 'HIGH',
        },
      ],
      subject_priorities: [
        {
          subject_id: 'sub-1',
          subject_name: 'Física',
          priority_score: 84.5,
          weighted_failure_rate: 0.75,
          upcoming_exam_days: 3,
          trend: 'REGRESSING',
          reasons: [
            'Tasa ponderada de fallo: 75% (4 intentos)',
            'Examen próximo en 3 días',
            'Tendencia en regresión reciente',
          ],
        },
      ],
      weak_exercise_types: [
        {
          exercise_type_id: 'ex-1',
          exercise_type_name: 'Plano inclinado',
          topic_name: 'Dinámica',
          subject_name: 'Física',
          attempts_count: 4,
          weighted_failure_rate: 0.75,
          dominant_error_cause: 'CONCEPT',
        },
      ],
    };

    render(
      <StudentDiagnosticPanel
        diagnostic={diagnostic}
        onStartRecordSession={vi.fn()}
      />
    );

    expect(screen.getAllByText('En regresión')).toHaveLength(2);
    expect(screen.getByText('Parcial Dinámica')).toBeInTheDocument();
    expect(screen.getByText('Riesgo alto')).toBeInTheDocument();
    expect(screen.getByText('84.5')).toBeInTheDocument();
    expect(
      screen.getByText('Tasa ponderada de fallo: 75% (4 intentos)')
    ).toBeInTheDocument();
    expect(screen.getByText('Examen próximo en 3 días')).toBeInTheDocument();
    expect(screen.getByText('Plano inclinado')).toBeInTheDocument();
    expect(screen.getByText('Concepto')).toBeInTheDocument();
  });

  it('invites recording the first session when diagnostic has no data yet', async () => {
    const user = userEvent.setup();
    const onStartRecordSession = vi.fn();

    const emptyDiagnostic: StudentDiagnostic = {
      student_id: 'stu-1',
      generated_at: '2026-11-16T00:00:00Z',
      analyzer_name: 'HeuristicPedagogicalAnalyzerV1',
      overall_trend: 'INSUFFICIENT_DATA',
      exam_alerts: [],
      subject_priorities: [],
      weak_exercise_types: [],
    };

    render(
      <StudentDiagnosticPanel
        diagnostic={emptyDiagnostic}
        onStartRecordSession={onStartRecordSession}
      />
    );

    expect(
      screen.getByText('Sin datos suficientes para diagnosticar todavía.')
    ).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Registrar primera clase' }));
    expect(onStartRecordSession).toHaveBeenCalledTimes(1);
  });
});
