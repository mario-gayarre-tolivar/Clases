import {
  ERROR_CAUSE_LABELS,
  RISK_LABELS,
  TREND_LABELS,
  formatPercent,
} from '../domain/labels';
import type { LearningTrend, ReadinessRisk, StudentDiagnostic } from '../domain/types';

export interface StudentDiagnosticPanelProps {
  diagnostic: StudentDiagnostic;
  onStartRecordSession: () => void;
}

function trendBadgeClass(trend: LearningTrend): string {
  switch (trend) {
    case 'IMPROVING':
      return 'badge badge--success';
    case 'REGRESSING':
      return 'badge badge--danger';
    case 'STAGNANT':
      return 'badge badge--warning';
    case 'INSUFFICIENT_DATA':
      return 'badge badge--neutral';
  }
}

function riskBadgeClass(risk: ReadinessRisk): string {
  switch (risk) {
    case 'HIGH':
      return 'badge badge--danger';
    case 'MEDIUM':
      return 'badge badge--warning';
    case 'LOW':
      return 'badge badge--success';
  }
}

function formatDaysRemaining(days: number): string {
  if (days === 0) return 'Hoy';
  if (days === 1) return 'En 1 día';
  return `En ${days} días`;
}

export function StudentDiagnosticPanel({
  diagnostic,
  onStartRecordSession,
}: StudentDiagnosticPanelProps) {
  const hasAnyContent =
    diagnostic.subject_priorities.length > 0 ||
    diagnostic.weak_exercise_types.length > 0 ||
    diagnostic.exam_alerts.length > 0;

  if (!hasAnyContent) {
    return (
      <div className="empty-state">
        <p className="empty-state__title">
          Sin datos suficientes para diagnosticar todavía.
        </p>
        <div className="empty-state__action">
          <button
            type="button"
            className="btn btn--primary"
            onClick={onStartRecordSession}
          >
            Registrar primera clase
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <span className="page-subtitle">Tendencia global: </span>
          <span className={trendBadgeClass(diagnostic.overall_trend)}>
            {TREND_LABELS[diagnostic.overall_trend]}
          </span>
        </div>
        <span className="page-subtitle">{diagnostic.analyzer_name}</span>
      </div>

      {diagnostic.exam_alerts.length > 0 && (
        <section aria-label="Alertas de examen" className="exam-alerts-strip">
          <h2 className="section-title">Exámenes próximos</h2>
          {diagnostic.exam_alerts.map((alert) => (
            <div key={alert.exam_goal_id} className="exam-alert-item">
              <div>
                <strong>{alert.title}</strong>{' '}
                <span className="page-subtitle">({alert.subject_name})</span>
              </div>
              <div>
                <span className="page-subtitle tabular" style={{ marginRight: '0.75rem' }}>
                  {formatDaysRemaining(alert.days_remaining)}
                </span>
                <span className={riskBadgeClass(alert.readiness_risk)}>
                  {RISK_LABELS[alert.readiness_risk]}
                </span>
              </div>
            </div>
          ))}
        </section>
      )}

      {diagnostic.subject_priorities.length > 0 && (
        <section aria-label="Prioridad por asignatura" className="section-block">
          <div className="section-header">
            <h2 className="section-title">Prioridad por asignatura</h2>
          </div>
          <div className="surface-panel table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">Asignatura</th>
                  <th scope="col">Prioridad</th>
                  <th scope="col">Tasa de fallo</th>
                  <th scope="col">Examen</th>
                  <th scope="col">Tendencia</th>
                  <th scope="col">Motivos</th>
                </tr>
              </thead>
              <tbody>
                {diagnostic.subject_priorities.map((item) => (
                  <tr key={item.subject_id}>
                    <td>
                      <strong>{item.subject_name}</strong>
                    </td>
                    <td className="tabular">
                      <strong>{item.priority_score}</strong>
                    </td>
                    <td className="tabular">
                      {formatPercent(item.weighted_failure_rate)}
                    </td>
                    <td className="tabular">
                      {item.upcoming_exam_days === null
                        ? '—'
                        : formatDaysRemaining(item.upcoming_exam_days)}
                    </td>
                    <td>
                      <span className={trendBadgeClass(item.trend)}>
                        {TREND_LABELS[item.trend]}
                      </span>
                    </td>
                    <td>
                      <ul className="reason-list">
                        {item.reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {diagnostic.weak_exercise_types.length > 0 && (
        <section aria-label="Tipos de ejercicio a reforzar" className="section-block">
          <div className="section-header">
            <h2 className="section-title">Ejercicios con mayor fallo</h2>
          </div>
          <div className="surface-panel table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">Ejercicio</th>
                  <th scope="col">Asignatura / Tema</th>
                  <th scope="col">Intentos</th>
                  <th scope="col">Tasa de fallo</th>
                  <th scope="col">Causa dominante</th>
                </tr>
              </thead>
              <tbody>
                {diagnostic.weak_exercise_types.map((ex) => (
                  <tr key={ex.exercise_type_id}>
                    <td>
                      <strong>{ex.exercise_type_name}</strong>
                    </td>
                    <td>
                      {ex.subject_name} / {ex.topic_name}
                    </td>
                    <td className="tabular">{ex.attempts_count}</td>
                    <td className="tabular">{formatPercent(ex.weighted_failure_rate)}</td>
                    <td>
                      {ex.dominant_error_cause ? (
                        <span className="badge badge--neutral">
                          {ERROR_CAUSE_LABELS[ex.dominant_error_cause]}
                        </span>
                      ) : (
                        'Sin especificar'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
