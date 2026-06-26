// Auto-generated from .telemetry/tracking-plan.yaml v1 — regenerar com a skill product-tracking-implement-tracking

export interface UserTraits {
  email?: string;          // PII — somente em identify()
  plan?: 'entry' | 'upsell' | 'subscription';
  purchased_at?: string;   // ISO 8601
  first_generate_at?: string;
  generate_count?: number;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
}

export interface CvGeneratedProps {
  job_area?: string | null;
  vaga_length_chars: number;
  experiencia_length_chars: number;
  duration_ms: number;
  success: boolean;
  error_type?: 'validation' | 'api_error' | 'timeout' | 'unexpected' | null;
}

export interface PurchaseCompletedProps {
  product_type: 'entry' | 'bump' | 'upsell' | 'downsell';
  amount_brl: number;
  payment_method?: 'credit_card' | 'pix' | 'boleto' | null;
  stripe_session_id: string;
}

export interface SubscriptionStartedProps {
  amount_brl: number;
  stripe_subscription_id: string;
}

export interface SubscriptionCancelledProps {
  reason?: 'user_cancelled' | 'payment_failed' | 'admin' | null;
  months_active?: number | null;
  stripe_subscription_id: string;
}
