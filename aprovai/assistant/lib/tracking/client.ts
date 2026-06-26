import { PostHog } from 'posthog-node';

let _ph: PostHog | null = null;

export function getPostHog(): PostHog {
  if (!_ph) {
    if (!process.env.POSTHOG_API_KEY) {
      throw new Error('POSTHOG_API_KEY não configurada');
    }
    _ph = new PostHog(process.env.POSTHOG_API_KEY, {
      host: 'https://us.i.posthog.com',
      flushAt: 1,       // flush imediato — obrigatório em Vercel serverless
      flushInterval: 0, // sem buffer; eventos são perdidos ao encerrar a função
    });
  }
  return _ph;
}

export async function flushPostHog(): Promise<void> {
  if (_ph) {
    await _ph.shutdown();
    _ph = null;
  }
}
