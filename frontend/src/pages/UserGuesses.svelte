<script>
  import { onMount, tick } from 'svelte';
  import { fade, scale, slide } from 'svelte/transition';
  import { userGuessStart, userGuessAsk, userGuessHint, userGuessGuess, userGuessGiveUp } from '../lib/api.js';

  export let navigate;

  // screen: 'start' | 'playing' | 'result'
  let screen   = 'start';
  let messages = [];      // { from: 'user'|'bot', text: string }
  let input    = '';
  let loading  = false;
  let error    = '';

  let questionsUsed      = 0;
  let questionsRemaining = 20;
  let penalty            = 0;
  let result             = null;   
  let guessInput         = '';
  let showGuessInput     = false;

  let chatContainer;

  async function scrollToBottom() {
    await tick();
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  function addMsg(from, text) {
    messages = [...messages, { from, text }];
    scrollToBottom();
  }

  async function start() {
    loading = true; error = '';
    try {
      const data = await userGuessStart();
      messages = [];
      addMsg('bot', data.message || "I'm thinking of something… Ask me YES/NO questions!");
      screen = 'playing';
      scrollToBottom();
    } catch (e) { error = e.message; }
    loading = false;
  }

  async function sendQuestion() {
    const q = input.trim();
    if (!q) return;
    input   = '';
    addMsg('user', q);
    loading = true;
    try {
      const data = await userGuessAsk(q);
      questionsUsed      = data.question_count    ?? questionsUsed + 1;
      questionsRemaining = data.questions_remaining ?? Math.max(0, questionsRemaining - 1);

      const answer = data.answer?.toUpperCase() ?? '—';
      const note   = data.understood === false ? ' (I didn\'t understand that question)' : '';
      addMsg('bot', `${answer}${note}`);
    } catch (e) { addMsg('bot', '⚠️ Error: ' + e.message); }
    loading = false;
    scrollToBottom();
  }

  async function getHint() {
    loading = true;
    try {
      const data = await userGuessHint();
      penalty = data.total_penalty ?? penalty;
      addMsg('bot', `💡 Hint: ${data.hint} (−${data.penalty} pts)`);
    } catch (e) { addMsg('bot', '⚠️ ' + e.message); }
    loading = false;
    scrollToBottom();
  }

  async function makeGuess() {
    const g = guessInput.trim();
    if (!g) return;
    loading = true; guessInput = ''; showGuessInput = false;
    addMsg('user', `My guess: ${g}`);
    try {
      const data = await userGuessGuess(g);
      result = data;
      screen = 'result';
    } catch (e) { addMsg('bot', '⚠️ ' + e.message); }
    loading = false;
  }

  async function giveUp() {
    loading = true;
    try {
      const data = await userGuessGiveUp();
      result = { ...data, correct: false, gave_up: true };
      screen = 'result';
    } catch (e) { error = e.message; }
    loading = false;
  }

  function reset() {
    screen = 'start'; messages = []; input = '';
    questionsUsed = 0; questionsRemaining = 20; penalty = 0;
    result = null; guessInput = ''; showGuessInput = false; error = '';
  }

  function onKeydown(e) {
    if (e.key === 'Enter' && !loading) sendQuestion();
  }
  function onGuessKeydown(e) {
    if (e.key === 'Enter' && !loading) makeGuess();
  }
</script>

<div class="page">
  <button class="back-btn" on:click={() => navigate('home')}>
    <span class="icon">←</span> Back
  </button>

  <div class="card" in:scale={{ duration: 400, start: 0.95 }}>
    <h2 class="page-title">🎯 You Guess</h2>

    {#if error}
      <div class="error-box" transition:slide>{error}</div>
    {/if}

    <!-- START -->
    {#if screen === 'start'}
      <div class="center-block" in:fade>
        <div class="big-icon neon-glow-user">🤔</div>
        <p class="lead">I'm thinking of a <strong>secret entity</strong>.</p>
        <p class="sub">Ask me up to 20 YES/NO questions, then make your guess!</p>
        <button class="btn-primary" on:click={start} disabled={loading}>
          {loading ? 'Initializing Core…' : "Let's Go!"}
          <div class="btn-glow"></div>
        </button>
      </div>

    <!-- PLAYING -->
    {:else if screen === 'playing'}
      <div class="hud" in:fade>
        <div class="hud-item">
          <span class="hud-icon">❓</span>
          <span class="hud-label">ASKED</span>
          <span class="hud-val highlight">{questionsUsed}</span>
        </div>
        <div class="hud-item">
          <span class="hud-icon">⏳</span>
          <span class="hud-label">LEFT</span>
          <span class="hud-val">{questionsRemaining}</span>
        </div>
        {#if penalty > 0}
          <div class="hud-item penalty" transition:fade>
            <span class="hud-icon">💸</span>
            <span class="hud-label">PENALTY</span>
            <span class="hud-val">−{penalty}</span>
          </div>
        {/if}
      </div>

      <div class="chat-wrap" bind:this={chatContainer} in:fade>
        {#each messages as m (m)}
          <div class="msg {m.from === 'user' ? 'msg-user' : 'msg-bot'}" in:slide={{ duration: 250 }}>
            <span class="avatar">{m.from === 'user' ? '🧑' : '🤖'}</span>
            <span class="bubble">{m.text}</span>
          </div>
        {/each}
        {#if loading}
          <div class="msg msg-bot" in:fade>
            <span class="avatar">🤖</span>
            <span class="bubble typing">PROCESSING</span>
          </div>
        {/if}
      </div>

      <div class="input-row" in:fade>
        <input
          class="chat-input"
          bind:value={input}
          on:keydown={onKeydown}
          placeholder="Transmit a YES/NO query…"
          disabled={loading}
          autofocus
        />
        <button class="send-btn" on:click={sendQuestion} disabled={loading || !input.trim()}>SEND</button>
      </div>

      {#if showGuessInput}
        <div class="guess-row" transition:slide={{ duration: 200 }}>
          <input
            class="chat-input target-input"
            bind:value={guessInput}
            on:keydown={onGuessKeydown}
            placeholder="Specify Target Entity…"
            disabled={loading}
            autofocus
          />
          <button class="send-btn confirm" on:click={makeGuess} disabled={loading || !guessInput.trim()}>✔</button>
          <button class="cancel-btn" on:click={() => { showGuessInput = false; guessInput = ''; }}>✕</button>
        </div>
      {/if}

      <div class="action-buttons" in:fade>
        <button class="btn-hint"    on:click={getHint}                         disabled={loading}>💡 SECURE HINT</button>
        <button class="btn-guess"   on:click={() => showGuessInput = true}     disabled={loading || showGuessInput}>🎯 LOCK GUESS</button>
        <button class="btn-giveup"  on:click={giveUp}                          disabled={loading}>🏳 ABORT</button>
      </div>

    <!-- RESULT -->
    {:else if screen === 'result'}
      <div class="center-block" in:fade>
        <div class="big-icon">{result?.correct ? '🏆' : result?.gave_up ? '😅' : '❌'}</div>
        <h3 class="result-title">
          {result?.correct ? 'You Nailed It!' : result?.gave_up ? 'Mission Aborted!' : 'Incorrect!'}
        </h3>
        <div class="secret-reveal" in:scale={{ duration: 500, start: 0.9 }}>
          The secret was: <strong>{result?.secret}</strong>
          {#if result?.category}<span class="category-badge">{result.category}</span>{/if}
        </div>
        {#if result?.score}
          <div class="score-display">
            <span>🤖 {result.score.ai_wins}</span>
            <span class="vs">vs</span>
            <span>🧑 {result.score.user_wins}</span>
          </div>
        {/if}
        {#if result?.questions_asked != null}
          <p class="sub">Data cost: {result.questions_asked} queries.</p>
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
    background: rgba(127, 0, 255, 0.05); 
    border: 1px solid rgba(127, 0, 255, 0.2); 
    color: var(--c-accent-light); 
    padding: 0.6rem 1.2rem; 
    border-radius: 12px; 
    cursor: pointer; 
    font-size: 0.95rem; font-weight: 600;
    transition: all 0.2s;
    backdrop-filter: blur(5px);
    display: flex; align-items: center; gap: 8px;
  }
  .back-btn:hover { background: rgba(127, 0, 255, 0.15); transform: translateX(-3px); }

  .card { 
    background: var(--c-card); border: 1px solid var(--c-card-border); 
    border-radius: 24px; padding: 2.5rem; width: 100%; max-width: 680px; 
    backdrop-filter: blur(20px); 
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
  }
  .page-title { 
    font-family: var(--font-display); color: var(--c-accent-light); 
    text-align: center; margin: 0 0 1.5rem; font-size: 1.8rem; font-weight: 800;
    text-shadow: 0 0 15px rgba(225,0,255,0.3);
  }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid rgba(255,60,60,0.4); color: #ff6b6b; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; font-size: 0.95rem; text-align: center; }

  .center-block { display: flex; flex-direction: column; align-items: center; gap: 1.2rem; text-align: center; }
  .big-icon { font-size: 4rem; animation: pulse 2.5s ease-in-out infinite; }
  .neon-glow-user { filter: drop-shadow(0 0 15px rgba(127, 0, 255, 0.5)); }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
  
  .lead { font-size: 1.1rem; color: var(--c-text); margin: 0; }
  .sub  { font-size: .95rem; color: var(--c-text-muted); margin: 0; }

  .hud { 
    display: flex; gap: 1rem; margin-bottom: 1.2rem; 
    background: rgba(0,0,0,0.2); padding: 0.8rem 1.2rem; 
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);
  }
  .hud-item { display: flex; align-items: center; gap: 6px; }
  .hud-icon { font-size: 1.1rem; }
  .hud-label { color: var(--c-text-muted); font-size: 0.75rem; font-weight: 700; letter-spacing: 1px;}
  .hud-val { font-size: 1.1rem; font-family: var(--font-display); font-weight: 700; color: var(--c-text); }
  .highlight { color: var(--c-accent-light); text-shadow: 0 0 10px rgba(225,0,255,0.4); }
  .penalty .hud-val { color: #ff4455; text-shadow: 0 0 10px rgba(255,68,85,0.4); }

  .chat-wrap { 
    display: flex; flex-direction: column; gap: 1rem; 
    height: 340px; overflow-y: auto; padding: 1rem; margin-bottom: 1.5rem; 
    background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(127,0,255,0.15); 
    border-radius: 16px; scroll-behavior: smooth;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
  }
  
  .msg { display: flex; align-items: flex-end; gap: .8rem; }
  .msg-user { flex-direction: row-reverse; }
  .avatar { font-size: 1.4rem; flex-shrink: 0; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); }
  
  .bubble { 
    padding: .8rem 1.1rem; border-radius: 16px; max-width: 85%; 
    line-height: 1.5; font-size: .95rem; font-weight: 500;
    position: relative; overflow: hidden;
  }
  .msg-user .bubble { 
    background: rgba(127, 0, 255, 0.15); border: 1px solid rgba(127, 0, 255, 0.3); 
    color: #f8f8ff; border-bottom-right-radius: 4px;
    box-shadow: 0 4px 15px rgba(127,0,255,0.1);
  }
  .msg-bot .bubble { 
    background: rgba(0, 242, 254, 0.1); border: 1px solid rgba(0, 242, 254, 0.2); 
    color: var(--c-text); border-bottom-left-radius: 4px;
    box-shadow: 0 4px 15px rgba(0,242,254,0.05);
  }
  
  .typing { letter-spacing: 2px; font-size: 0.8rem; font-weight: 700; color: var(--c-primary); animation: blink 1.2s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }

  .input-row, .guess-row { display: flex; gap: .6rem; margin-bottom: 1rem; }
  .chat-input { 
    flex: 1; background: rgba(0,0,0,0.3); 
    border: 1px solid rgba(127,0,255,0.3); color: #fff; 
    padding: 0.9rem 1.2rem; border-radius: 12px; font-size: 1rem; outline: none; 
    transition: all 0.2s; font-family: var(--font-body);
  }
  .chat-input:focus { border-color: var(--c-accent-light); box-shadow: 0 0 15px rgba(225,0,255,0.2); background: rgba(0,0,0,0.5); }
  .target-input { border-color: #00ff88; }
  .target-input:focus { border-color: #00ff88; box-shadow: 0 0 15px rgba(0,255,136,0.2); }

  .send-btn { 
    background: linear-gradient(135deg, var(--c-accent), var(--c-accent-light)); 
    color: #fff; border: none; border-radius: 12px; padding: 0 1.5rem; 
    cursor: pointer; font-weight: 700; font-size: 0.9rem; letter-spacing: 1px;
    transition: all 0.2s;
  }
  .send-btn:hover { filter: brightness(1.2); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(225,0,255,0.3); }
  .send-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; box-shadow: none; filter: none; }
  
  .send-btn.confirm { background: linear-gradient(135deg, #00cc66, #00ff88); color: #000; box-shadow: 0 5px 15px rgba(0,255,136,0.3); }
  
  .cancel-btn { background: transparent; border: 1px solid rgba(255,255,255,.2); color: var(--c-text-muted); border-radius: 12px; padding: 0 1.2rem; cursor: pointer; transition: all 0.2s; }
  .cancel-btn:hover { background: rgba(255,68,85,0.1); color: #ff4455; border-color: rgba(255,68,85,0.3); }

  .action-buttons { display: flex; gap: .8rem; flex-wrap: wrap; }
  .btn-hint, .btn-guess, .btn-giveup { 
    flex: 1; padding: 0.9rem; border: none; border-radius: 12px; font-size: 0.85rem; 
    cursor: pointer; font-weight: 700; transition: all .2s; min-width: 120px; letter-spacing: 1px;
  }
  .btn-hint:hover, .btn-guess:hover, .btn-giveup:hover { transform: translateY(-3px); }
  .btn-hint:disabled, .btn-guess:disabled, .btn-giveup:disabled { opacity: .4; cursor: not-allowed; transform: none; box-shadow:none; }
  
  .btn-hint   { background: rgba(255,200,0,.1); border: 1px solid rgba(255,200,0,.4); color: #ffd700; }
  .btn-hint:hover { background: rgba(255,200,0,.2); box-shadow: 0 5px 15px rgba(255,200,0,.2); }
  .btn-guess  { background: linear-gradient(135deg, var(--c-accent), var(--c-accent-light)); color: #fff; border: 1px solid transparent; }
  .btn-guess:hover { box-shadow: 0 5px 15px rgba(225,0,255,.4); }
  .btn-giveup { background: rgba(255,60,60,.1); border: 1px solid rgba(255,60,60,.4); color: #ff4455; }
  .btn-giveup:hover { background: rgba(255,60,60,.2); box-shadow: 0 5px 15px rgba(255,68,85,.2); }

  .secret-reveal { 
    font-size: 1.3rem; color: var(--c-text); background: rgba(127,0,255,0.08);
    padding: 1.5rem 2rem; border-radius: 16px; border: 1px solid rgba(127,0,255,0.2);
    margin: 1rem 0;
  }
  .secret-reveal strong { color: var(--c-accent-light); font-size: 1.8rem; font-family: var(--font-display); display: block; margin-top: 0.5rem; text-shadow: 0 0 15px rgba(225,0,255,0.3); }
  .category-badge { background: rgba(127,0,255,.15); border: 1px solid rgba(127,0,255,.3); color: var(--c-accent-light); font-size: .8rem; font-family: var(--font-body); padding: .2rem .6rem; border-radius: 8px; margin-left: .5rem; vertical-align: middle; }
  
  .result-title { font-size: 1.8rem; font-family: var(--font-display); color: var(--c-accent-light); margin: 0; }
  .score-display { display: flex; gap: 1.5rem; align-items: center; font-size: 1.6rem; font-family: var(--font-display); font-weight: 700; color: var(--c-text); background: rgba(0,0,0,0.3); padding: 1rem 2rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
  .vs { color: var(--c-text-muted); font-size: 1.1rem; }
  .result-actions { display: flex; gap: 1.2rem; justify-content: center; }

  .btn-primary { 
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, var(--c-accent), var(--c-accent-light)); 
    color: #fff; border: none; border-radius: 12px; 
    padding: 0.9rem 2.2rem; font-size: 1.05rem; font-weight: 700; 
    cursor: pointer; transition: transform .2s; 
  }
  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(225,0,255,0.3); filter: brightness(1.1); }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; }
  
  .btn-glow {
    position: absolute; inset: 0; opacity: 0; transition: opacity 0.3s;
    background: radial-gradient(circle at top, rgba(255,255,255,0.4) 0%, transparent 70%);
  }
  .btn-primary:hover .btn-glow { opacity: 1; }

  .btn-secondary { background: transparent; border: 1px solid var(--c-card-border); color: var(--c-text); border-radius: 12px; padding: 0.9rem 2.2rem; font-size: 1.05rem; font-weight: 600; cursor: pointer; transition: all .2s; }
  .btn-secondary:hover { background: rgba(255,255,255,0.05); color: var(--c-accent-light); border-color: rgba(225,0,255,0.3); }
</style>
