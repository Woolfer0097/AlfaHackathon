export interface Client {
  id: number;
  full_name: string;
  age: number | null;
  city: string | null;
  segment: string | null;
  products: string[];
  risk_score: number;
  // Additional fields from backend
  adminarea?: string | null;
  gender?: string | null;
  incomeValue?: number | null;
  incomeValueCategory?: string | null;
}

export interface IncomePrediction {
  predicted_income: number;
  lower_bound: number;
  upper_bound: number;
  base_income?: number;
}

export interface ShapFeature {
  feature_name: string;
  value: number | string;
  shap_value: number;
  direction: 'positive' | 'negative';
  description?: string;
}

export interface ShapResponse {
  text_explanation: string;
  features: ShapFeature[];
  base_value?: number;
}

export interface Recommendation {
  id: number;
  product_name: string;
  product_type: 'credit' | 'credit_card' | 'deposit' | 'insurance';
  limit?: number;
  rate?: number;
  reason: string;
  description?: string;
}

export interface TrainingRun {
  model_version: string;
  trained_at: string;
  train_samples: number;
  valid_samples: number;
  rmse: number;
  mae: number;
  r2: number;
}

export interface ModelMetrics {
  wmae_validation: number;
  training_records: number;
  validation_records: number;
  predictions_count: number;
  experiments: Experiment[];
  segment_errors: SegmentError[];
  training_runs?: TrainingRun[];
}

export interface Experiment {
  name: string;
  wmae: number;
  date?: string;
}

export interface SegmentError {
  segment: string;
  wmae: number;
}

