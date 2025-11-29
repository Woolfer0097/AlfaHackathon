export interface Client {
  id: number;
  full_name: string;
  age: number;
  city: string;
  segment: string;
  products: string[];
  risk_score: number;
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

export interface ModelMetrics {
  wmae_validation: number;
  training_records: number;
  validation_records: number;
  predictions_count: number;
  experiments: Experiment[];
  segment_errors: SegmentError[];
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

