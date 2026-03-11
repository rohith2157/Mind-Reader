const BASE = '';   // Vite proxies /api/* → Flask in dev; same-origin in prod

async function post(path, body = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// ── AI Guesses ────────────────────────────────────────────────
export const aiGuessStart    = ()                   => post('/api/ai-guess/start');
export const aiGuessAnswer   = (feature, answer)    => post('/api/ai-guess/answer', { feature, answer });
export const aiGuessFinalize = (correct)            => post('/api/ai-guess/finalize', { correct });

// ── User Guesses ──────────────────────────────────────────────
export const userGuessStart  = ()            => post('/api/user-guess/start');
export const userGuessAsk    = (question)    => post('/api/user-guess/ask', { question });
export const userGuessHint   = ()            => post('/api/user-guess/hint');
export const userGuessGuess  = (entity)      => post('/api/user-guess/guess', { entity });
export const userGuessGiveUp = ()            => post('/api/user-guess/give-up');

// ── Meta ──────────────────────────────────────────────────────
export const getStats = () => get('/api/stats');
export const getScore = () => get('/api/score');
