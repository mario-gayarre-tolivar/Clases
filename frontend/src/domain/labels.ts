import type {
  AttemptOutcome,
  ErrorCause,
  LearningTrend,
  ReadinessRisk,
} from './types';

export const OUTCOME_LABELS: Record<AttemptOutcome, string> = {
  SUCCESS: 'Acierto',
  PARTIAL: 'Parcial',
  FAILURE: 'Fallo',
};

export const ERROR_CAUSE_LABELS: Record<ErrorCause, string> = {
  CONCEPT: 'Concepto',
  CALCULATION: 'Cálculo',
  COMPREHENSION: 'Comprensión',
  CARELESSNESS: 'Despiste',
};

export const TREND_LABELS: Record<LearningTrend, string> = {
  IMPROVING: 'En mejora',
  STAGNANT: 'Estancado',
  REGRESSING: 'En regresión',
  INSUFFICIENT_DATA: 'Datos insuficientes',
};

export const RISK_LABELS: Record<ReadinessRisk, string> = {
  HIGH: 'Riesgo alto',
  MEDIUM: 'Riesgo medio',
  LOW: 'Riesgo bajo',
};

export function formatPercent(rate: number): string {
  return `${Math.round(rate * 100)}%`;
}
