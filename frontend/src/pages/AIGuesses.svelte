<script>
  import { onMount } from 'svelte';
  import { slide, scale, fade } from 'svelte/transition';
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
  <button class="back-btn" on:click={() => navigate('home')}>
    <span class="icon">←</span> Back
  </button>

  <div class="card" in:scale={{ duration: 400, start: 0.95 }}>
    <h2 class="page-title">🤖 AI Guesses</h2>

    {#if error}
      <div class="error-box" transition:slide>{error}</div>
    {/if}

    <!-- START -->
    {#if screen === 'start'}
      <div class="center-block" in:fade>
        <div class="big-icon neon-glow">🧠</div>
        <p class="lead">Think of an <strong>animal, food, sport, vehicle, or musical instrument</strong>.</p>
        <p class="sub">Keep it in your head — the AI will ask YES/NO questions and try to figure it out!</p>
        <button class="btn-primary" on:click={start} disabled={loading}>
          {loading ? 'Initializing Interface…' : "I'm Ready — Start!"}
          <div class="btn-glow"></div>
        </button>
      </div>

    <!-- PLAYING -->
    {:else if screen === 'playing'}
      <div class="confidence-wrap" in:fade>
        <div class="conf-label">AI CERTAINTY</div>
        <div class="conf-bar-bg">
          <div class="conf-bar" style="width:{certainty}%"></div>
        </div>
        <div class="conf-pct">{certainty}%</div>
      </div>

      <div class="candidates-row" in:fade>
        {#each candidates as c (c)}
          <span class="candidate-chip" animate:fade out:scale={{ duration: 200, start: 0.8 }}>{c}</span>
        {/each}
      </div>

      <div class="question-box" in:slide>
        <div class="q-label">INCOMING TRANSMISSION / QUESTION</div>
        <div class="q-text">{question}</div>
      </div>

      <div class="answer-buttons" in:fade>
        <button class="btn-yes" on:click={() => answer('yes')} disabled={loading}>
          <span>✅ YES</span>
        </button>
        <button class="btn-no" on:click={() => answer('no')} disabled={loading}>
          <span>❌ NO</span>
        </button>
      </div>

    <!-- GUESS -->
    {:else if screen === 'guess'}
      <div class="center-block" in:fade>
        <div class="big-icon neon-glow-target">🎯</div>
        <p class="lead">The AI thinks you are thinking of…</p>
        <div class="guess-reveal" in:scale={{ duration: 500, start: 0.8 }}>{guess}</div>
        <p class="sub">Is the AI correct?</p>
        <div class="answer-buttons">
          <button class="btn-yes" on:click={() => finalize(true)} disabled={loading}>✅ Correct!</button>
          <button class="btn-no"  on:click={() => finalize(false)} disabled={loading}>❌ Wrong!</button>
        </div>
      </div>

    <!-- RESULT -->
    {:else if screen === 'result'}
      <div class="center-block" in:fade>
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
  .page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; position: relative; z-index: 10; }
  
  .back-btn { 
    position: fixed; top: 1.5rem; left: 1.5rem; 
    background: rgba(0, 242, 254, 0.05); 
    border: 1px solid rgba(0, 242, 254, 0.2); 
    color: var(--c-primary); 
    padding: 0.6rem 1.2rem; 
    border-radius: 12px; 
    cursor: pointer; 
    font-size: 0.95rem; font-weight: 600;
    transition: all 0.2s;
    backdrop-filter: blur(5px);
    display: flex; align-items: center; gap: 8px;
  }
  .back-btn:hover { background: rgba(0, 242, 254, 0.15); transform: translateX(-3px); }

  .card { 
    background: var(--c-card); 
    border: 1px solid var(--c-card-border); 
    border-radius: 24px; 
    padding: 3rem; 
    width: 100%; max-width: 680px; 
    backdrop-filter: blur(20px); 
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
  }
  .page-title { 
    font-family: var(--font-display);
    color: var(--c-primary); 
    text-align: center; margin: 0 0 2rem; font-size: 2rem; font-weight: 800;
    text-shadow: 0 0 15px rgba(0,242,254,0.3);
  }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid rgba(255,60,60,0.4); color: #ff6b6b; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; font-size: 0.95rem; text-align: center; }

  .center-block { display: flex; flex-direction: column; align-items: center; gap: 1.2rem; text-align: center; }
  .big-icon { font-size: 4rem; animation: pulse 2.5s ease-in-out infinite; filter: drop-shadow(0 0 15px rgba(0, 242, 254, 0.4)); }
  .neon-glow-target { filter: drop-shadow(0 0 15px rgba(225, 0, 255, 0.5)); }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
  
  .lead  { font-size: 1.1rem; color: var(--c-text); margin: 0; }
  .sub   { font-size: .95rem; color: var(--c-text-muted); margin: 0; }

  .confidence-wrap { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; background: rgba(0,0,0,0.2); padding: 0.8rem 1.2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
  .conf-label { color: var(--c-text-muted); font-size: .75rem; font-weight: 700; white-space: nowrap; letter-spacing: 1px;}
  .conf-bar-bg { flex: 1; height: 8px; background: rgba(255,255,255,.05); border-radius: 4px; overflow: hidden; }
  .conf-bar { height: 100%; background: linear-gradient(90deg, var(--c-primary), var(--c-accent-light)); border-radius: 4px; transition: width .6s cubic-bezier(0.2, 0.8, 0.2, 1); box-shadow: 0 0 10px rgba(0,242,254,0.5); }
  .conf-pct { color: var(--c-primary); font-size: .9rem; font-weight: 700; width: 36px; text-align: right; }

  .candidates-row { 
    display: flex; flex-wrap: wrap; gap: .5rem; 
    max-height: 140px; overflow-y: auto; 
    margin-bottom: 1.5rem; padding: 0.5rem;
    background: rgba(0,0,0,0.15);
    border-radius: 12px;
    border: 1px solid rgba(0,242,254,0.1);
  }
  .candidate-chip { 
    background: rgba(0, 242, 254, 0.08); 
    border: 1px solid rgba(0, 242, 254, 0.25); 
    color: var(--c-primary); font-size: .8rem; font-weight: 500;
    padding: .3rem .7rem; border-radius: 8px;
    transition: all 0.2s;
  }
  
  .question-box { 
    background: rgba(0, 242, 254, 0.05); 
    border: 1px solid rgba(0, 242, 254, 0.2); 
    border-radius: 16px; padding: 1.5rem 1.8rem; margin-bottom: 2rem; 
    position: relative; overflow: hidden;
  }
  .question-box::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--c-primary);
  }
  .q-label { color: var(--c-primary); font-size: .75rem; font-weight: 700; letter-spacing: 1.5px; margin-bottom: .8rem; }
  .q-text  { font-size: 1.3rem; font-weight: 500; color: var(--c-text); line-height: 1.4; }

  .answer-buttons { display: flex; gap: 1.2rem; width: 100%; }
  .btn-yes, .btn-no { 
    flex: 1; padding: 1.1rem; border: none; border-radius: 14px; 
    font-size: 1.1rem; font-family: var(--font-display); font-weight: 700; 
    cursor: pointer; transition: all .2s; 
    position: relative; overflow: hidden;
  }
  .btn-yes:hover, .btn-no:hover { transform: translateY(-3px); }
  .btn-yes:disabled, .btn-no:disabled { opacity: .5; cursor: not-allowed; transform: none; }
  
  .btn-yes { background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.4); color: #00ff88; }
  .btn-yes:hover { background: rgba(0, 255, 136, 0.2); box-shadow: 0 0 20px rgba(0, 255, 136, 0.2); }
  .btn-no  { background: rgba(255, 68, 85, 0.1); border: 1px solid rgba(255, 68, 85, 0.4); color: #ff4455; }
  .btn-no:hover { background: rgba(255, 68, 85, 0.2); box-shadow: 0 0 20px rgba(255, 68, 85, 0.2); }

  .guess-reveal { 
    font-size: 2.5rem; font-family: var(--font-display); font-weight: 800; 
    background: linear-gradient(135deg, var(--c-primary), var(--c-accent-light));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 2px; padding: 1.5rem 3rem; 
    border: 1px solid rgba(225,0,255,0.3); border-radius: 20px; 
    background-color: rgba(225,0,255,0.05);
    box-shadow: 0 0 30px rgba(225,0,255,0.1);
  }

  .result-title { font-family: var(--font-display); font-size: 1.8rem; color: var(--c-primary); margin: 0; }
  .score-display { display: flex; gap: 1.5rem; align-items: center; font-size: 1.6rem; font-family: var(--font-display); font-weight: 700; color: var(--c-text); background: rgba(0,0,0,0.3); padding: 1rem 2rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
  .vs { color: var(--c-text-muted); font-size: 1.1rem; }
  .result-actions { display: flex; gap: 1.2rem; width: 100%; justify-content: center; }

  .btn-primary { 
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark)); 
    color: #000; border: none; border-radius: 12px; 
    padding: 0.9rem 2.2rem; font-size: 1.05rem; font-weight: 700; 
    cursor: pointer; transition: transform .2s; 
  }
  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,242,254,0.3); }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; }
  
  .btn-glow {
    position: absolute; inset: 0; opacity: 0; transition: opacity 0.3s;
    background: radial-gradient(circle at top, rgba(255,255,255,0.5) 0%, transparent 70%);
  }
  .btn-primary:hover .btn-glow { opacity: 1; }

  .btn-secondary { 
    background: transparent; border: 1px solid var(--c-card-border); 
    color: var(--c-text); border-radius: 12px; 
    padding: 0.9rem 2.2rem; font-size: 1.05rem; font-weight: 600; cursor: pointer; transition: all .2s; 
  }
  .btn-secondary:hover { background: rgba(255,255,255,0.05); color: var(--c-primary); border-color: rgba(0,242,254,0.3); }
</style>
