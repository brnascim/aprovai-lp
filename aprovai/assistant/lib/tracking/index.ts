export { getPostHog, flushPostHog } from './client';
export type {
  UserTraits,
  CvGeneratedProps,
  PurchaseCompletedProps,
  SubscriptionStartedProps,
  SubscriptionCancelledProps,
} from './types';

import { getPostHog, flushPostHog } from './client';
import type { CvGeneratedProps } from './types';

export const EVENTS = {
  CV_GENERATED:            'cv.generated',
  PURCHASE_COMPLETED:      'purchase.completed',
  SUBSCRIPTION_STARTED:    'subscription.started',
  SUBSCRIPTION_CANCELLED:  'subscription.cancelled',
  LP_VIEWED:               'lp.viewed',
  CHECKOUT_STARTED:        'checkout.started',
  MOTOR_ACCESSED:          'motor.accessed',
} as const;

export async function trackCvGenerated(
  distinctId: string,
  props: CvGeneratedProps,
): Promise<void> {
  const ph = getPostHog();
  ph.capture({
    distinctId,
    event: EVENTS.CV_GENERATED,
    properties: {
      job_area:                 props.job_area ?? null,
      vaga_length_chars:        props.vaga_length_chars,
      experiencia_length_chars: props.experiencia_length_chars,
      duration_ms:              props.duration_ms,
      success:                  props.success,
      error_type:               props.error_type ?? null,
      ...(props.success && {
        $set_once: { first_generate_at: new Date().toISOString() },
      }),
    },
  });
  await flushPostHog();
}
