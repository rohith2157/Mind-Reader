<script>
  import { onMount } from 'svelte';
  import { aiGuessStart, aiGuessAnswer, aiGuessFinalize } from '../lib/api.js';

  export let navigate;

  // screen: 'start' | 'playing' | 'guess' | 'result'
  let screen     = 'start';
  let question   = '';    // display text
  let feature    = '';    // internal feature key to send back
  let candidates = [];
  let guess      = '';
  let guessResult = '';   // 'correct' | 'wrong'
  let score      = null;
  let loading    = false;
  let error      = '';
  let certainty  = 0;     // AI Certainty percentage (0-100)

  async function start() {
    loading = true; error = '';
    try {
      const data = await aiGuessStart();
      question   = data.question?.question ?? data.question;
      feature    = data.question?.feature  ?? '';
      candidates = data.candidates || [];
      certainty  = 0;
      screen     = 'playing';
    } catch (e) { error = e.message; }
    loading = false;
  }

  async function answer(ans) {
    loading = true; error = '';
    try {
      const data = await aiGuessAnswer(feature, ans);
      candidates = data.candidates || candidates;
      
      if (data.result && data.result.confidence !== undefined) {
        certainty = Math.round(data.result.confidence);
      }

      if (data.status === 'guessing') {
        guess  = data.guess?.guess ?? data.guess;
        certainty = 99; // Approaching 100% when guessing
        screen = 'guess';
      } else {
        question = data.question?.question ?? data.question;
        feature  = data.question?.feature  ?? feature;
      }
    } catch (e) { error = e.message; }
    loading = false;
  }

  async function finalize(correct) {
    loading = true; error = '';
    try {
      const data = await aiGuessFinalize(correct);
      score       = data.score;
      guessResult = correct ? 'correct' : 'wrong';
      screen      = 'result';
    } catch (e) { error = e.message; }
    loading = false;
  }

  function reset() {
    screen = 'start'; question = ''; candidates = [];
    guess = ''; guessResult = ''; score = null; error = '';
  }

</script>

<div class="page">
  <button class="back-btn" on:click={() => navigate('home')}>← Back</button>

  <div class="card">
    <h2 class="page-title">🤖 AI Guesses</h2>

    {#if error}
      <div class="error-box">{error}</div>
    {/if}

    <!-- START -->
    {#if screen === 'start'}
      <div class="center-block">
        <div class="big-icon">🧠</div>
        <p class="lead">Think of an <strong>animal, food, sport, vehicle, or musical instrument</strong>.</p>
        <p class="sub">Keep it in your head — the AI will ask YES/NO questions and try to figure it out!</p>
        <button class="btn-primary" on:click={start} disabled={loading}>
          {loading ? 'Loading…' : "I'm Ready — Start!"}
        </button>
      </div>

    <!-- PLAYING -->
    {:else if screen === 'playing'}
      <div class="confidence-wrap">
        <div class="conf-label">AI Certainty</div>
        <div class="conf-bar-bg">
          <div class="conf-bar" style="width:{certainty}%"></div>
        </div>
        <div class="conf-pct">{certainty}%</div>
      </div>

      <div class="candidates-row">
        {#each candidates as c}
          <span class="candidate-chip">{c}</span>
        {/each}
      </div>

      <div class="question-box">
        <div class="q-label">Question</div>
        <div class="q-text">{question}</div>
      </div>

      <div class="answer-buttons">
        <button class="btn-yes" on:click={() => answer('yes')} disabled={loading}>
          ✅ YES
        </button>
        <button class="btn-no" on:click={() => answer('no')} disabled={loading}>
          ❌ NO
        </button>
      </div>

    <!-- GUESS -->
    {:else if screen === 'guess'}
      <div class="center-block">
        <div class="big-icon">🎯</div>
        <p class="lead">The AI thinks you are thinking of…</p>
        <div class="guess-reveal">{guess}</div>
        <p class="sub">Is the AI correct?</p>
        <div class="answer-buttons">
          <button class="btn-yes" on:click={() => finalize(true)} disabled={loading}>✅ Correct!</button>
          <button class="btn-no"  on:click={() => finalize(false)} disabled={loading}>❌ Wrong!</button>
        </div>
      </div>

    <!-- RESULT -->
    {:else if screen === 'result'}
      <div class="center-block">
        <div class="big-icon">{guessResult === 'correct' ? '🏆' : '😅'}</div>
        <h3 class="result-title">
          {guessResult === 'correct' ? 'AI Got It Right!' : 'You Stumped the AI!'}
        </h3>
        {#if score}
          <div class="score-display">
            <span>🤖 {score.ai_wins}</span>
            <span class="vs">vs</span>
            <span>🧑 {score.user_wins}</span>
          </div>
        {/if}
        <div class="result-actions">
          <button class="btn-primary" on:click={reset}>Play Again</button>
          <button class="btn-secondary" on:click={() => navigate('home')}>Home</button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; }
  .back-btn { position: fixed; top: 1.2rem; left: 1.2rem; background: rgba(0,255,136,.1); border: 1px solid rgba(0,255,136,.3); color: #00ff88; padding: .5rem 1rem; border-radius: 8px; cursor: pointer; font-size: .9rem; }
  .back-btn:hover { background: rgba(0,255,136,.2); }

  .card { background: rgba(0,0,0,.8); border: 1px solid rgba(0,255,136,.25); border-radius: 20px; padding: 2.5rem; width: 100%; max-width: 620px; backdrop-filter: blur(8px); }
  .page-title { color: #00ff88; text-align: center; margin: 0 0 1.5rem; font-size: 1.7rem; }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid #ff3c3c; color: #ff6b6b; border-radius: 8px; padding: .8rem 1rem; margin-bottom: 1rem; font-size: .9rem; }

  .center-block { display: flex; flex-direction: column; align-items: center; gap: 1rem; text-align: center; }
  .big-icon { font-size: 3.5rem; animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }
  .lead  { font-size: 1.05rem; color: #ddd; margin: 0; }
  .sub   { font-size: .9rem; color: #888; margin: 0; }

  .confidence-wrap { display: flex; align-items: center; gap: .8rem; margin-bottom: 1.2rem; }
  .conf-label { color: #888; font-size: .8rem; white-space: nowrap; }
  .conf-bar-bg { flex: 1; height: 10px; background: rgba(255,255,255,.1); border-radius: 5px; overflow: hidden; }
  .conf-bar { height: 100%; background: linear-gradient(90deg, #00ff88, #00ccff); border-radius: 5px; transition: width .5s ease; }
  .conf-pct { color: #00ff88; font-size: .8rem; font-weight: 700; width: 32px; text-align: right; }

  .candidates-row { display: flex; flex-wrap: wrap; gap: .4rem; max-height: 120px; overflow-y: auto; margin-bottom: 1.2rem; padding-right: 4px; }
  .candidate-chip { background: rgba(0,255,136,.1); border: 1px solid rgba(0,255,136,.25); color: #00ff88; font-size: .75rem; padding: .2rem .6rem; border-radius: 12px; }
  .candidate-chip.more { background: rgba(0,170,255,.1); border-color: rgba(0,170,255,.25); color: #00aaff; }

  .question-box { background: rgba(0,255,136,.06); border: 1px solid rgba(0,255,136,.2); border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; }
  .q-label { color: #00ff88; font-size: .75rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: .5rem; }
  .q-text  { font-size: 1.15rem; color: #eee; }

  .answer-buttons { display: flex; gap: 1rem; }
  .btn-yes, .btn-no { flex: 1; padding: .9rem; border: none; border-radius: 12px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: transform .1s; }
  .btn-yes:hover, .btn-no:hover { transform: scale(1.04); }
  .btn-yes:disabled, .btn-no:disabled { opacity: .5; cursor: not-allowed; transform: none; }
  .btn-yes { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; }
  .btn-no  { background: linear-gradient(135deg, #ff4455, #cc2233); color: #fff; }

  .guess-reveal { font-size: 2.2rem; font-weight: 700; color: #00ff88; letter-spacing: 2px; padding: 1rem 2rem; border: 2px solid rgba(0,255,136,.35); border-radius: 14px; background: rgba(0,255,136,.06); }

  .result-title { font-size: 1.5rem; color: #00ff88; margin: 0; }
  .score-display { display: flex; gap: 1rem; align-items: center; font-size: 1.4rem; font-weight: 700; color: #00ff88; }
  .vs { color: #555; font-size: 1rem; }
  .result-actions { display: flex; gap: 1rem; }

  .btn-primary { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; border: none; border-radius: 10px; padding: .8rem 1.8rem; font-size: 1rem; font-weight: 700; cursor: pointer; transition: transform .1s; }
  .btn-primary:hover { transform: scale(1.04); }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; }
  .btn-secondary { background: transparent; border: 1px solid rgba(0,255,136,.3); color: #00ff88; border-radius: 10px; padding: .8rem 1.8rem; font-size: 1rem; cursor: pointer; }
  .btn-secondary:hover { background: rgba(0,255,136,.1); }
</style>
