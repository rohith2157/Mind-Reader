<script>
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
  let result             = null;   // { correct, secret, questions_asked, score } | { secret, category, score }
  let guessInput         = '';
  let showGuessInput     = false;

  function addMsg(from, text) {
    messages = [...messages, { from, text }];
  }

  async function start() {
    loading = true; error = '';
    try {
      const data = await userGuessStart();
      addMsg('bot', data.message || "I'm thinking of something… Ask me YES/NO questions!");
      screen = 'playing';
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
  }

  async function getHint() {
    loading = true;
    try {
      const data = await userGuessHint();
      penalty = data.total_penalty ?? penalty;
      addMsg('bot', `💡 Hint: ${data.hint} (−${data.penalty} pts)`);
    } catch (e) { addMsg('bot', '⚠️ ' + e.message); }
    loading = false;
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
  <button class="back-btn" on:click={() => navigate('home')}>← Back</button>

  <div class="card">
    <h2 class="page-title">🎯 You Guess</h2>

    {#if error}
      <div class="error-box">{error}</div>
    {/if}

    <!-- START -->
    {#if screen === 'start'}
      <div class="center-block">
        <div class="big-icon">🤔</div>
        <p class="lead">I'm thinking of a <strong>secret entity</strong>.</p>
        <p class="sub">Ask me up to 20 YES/NO questions, then make your guess!</p>
        <button class="btn-primary" on:click={start} disabled={loading}>
          {loading ? 'Loading…' : "Let's Go!"}
        </button>
      </div>

    <!-- PLAYING -->
    {:else if screen === 'playing'}
      <div class="hud">
        <span>❓ <strong>{questionsUsed}</strong> asked</span>
        <span>⏳ <strong>{questionsRemaining}</strong> left</span>
        {#if penalty > 0}<span>💸 Penalty: <strong>−{penalty}</strong></span>{/if}
      </div>

      <div class="chat-wrap">
        {#each messages as m}
          <div class="msg {m.from === 'user' ? 'msg-user' : 'msg-bot'}">
            <span class="avatar">{m.from === 'user' ? '🧑' : '🤖'}</span>
            <span class="bubble">{m.text}</span>
          </div>
        {/each}
        {#if loading}
          <div class="msg msg-bot">
            <span class="avatar">🤖</span>
            <span class="bubble typing">…</span>
          </div>
        {/if}
      </div>

      <div class="input-row">
        <input
          class="chat-input"
          bind:value={input}
          on:keydown={onKeydown}
          placeholder="Ask a yes/no question…"
          disabled={loading}
        />
        <button class="send-btn" on:click={sendQuestion} disabled={loading || !input.trim()}>Send</button>
      </div>

      {#if showGuessInput}
        <div class="guess-row">
          <input
            class="chat-input"
            bind:value={guessInput}
            on:keydown={onGuessKeydown}
            placeholder="Type your final guess…"
            disabled={loading}
          />
          <button class="send-btn confirm" on:click={makeGuess} disabled={loading || !guessInput.trim()}>✔</button>
          <button class="cancel-btn" on:click={() => { showGuessInput = false; guessInput = ''; }}>✕</button>
        </div>
      {/if}

      <div class="action-buttons">
        <button class="btn-hint"    on:click={getHint}                         disabled={loading}>💡 Hint</button>
        <button class="btn-guess"   on:click={() => showGuessInput = true}     disabled={loading || showGuessInput}>🎯 Make Guess</button>
        <button class="btn-giveup"  on:click={giveUp}                          disabled={loading}>🏳 Give Up</button>
      </div>

    <!-- RESULT -->
    {:else if screen === 'result'}
      <div class="center-block">
        <div class="big-icon">{result?.correct ? '🏆' : result?.gave_up ? '😅' : '❌'}</div>
        <h3 class="result-title">
          {result?.correct ? 'You Got It!' : result?.gave_up ? 'Better luck next time!' : 'Not quite!'}
        </h3>
        <div class="secret-reveal">
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
          <p class="sub">You asked {result.questions_asked} questions.</p>
        {/if}
        <div class="result-actions">
          <button class="btn-primary"   on:click={reset}>Play Again</button>
          <button class="btn-secondary" on:click={() => navigate('home')}>Home</button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; }
  .back-btn { position: fixed; top: 1.2rem; left: 1.2rem; background: rgba(0,170,255,.1); border: 1px solid rgba(0,170,255,.3); color: #00aaff; padding: .5rem 1rem; border-radius: 8px; cursor: pointer; font-size: .9rem; }
  .back-btn:hover { background: rgba(0,170,255,.2); }

  .card { background: rgba(0,0,0,.8); border: 1px solid rgba(0,170,255,.25); border-radius: 20px; padding: 2rem; width: 100%; max-width: 620px; backdrop-filter: blur(8px); }
  .page-title { color: #00aaff; text-align: center; margin: 0 0 1.5rem; font-size: 1.7rem; }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid #ff3c3c; color: #ff6b6b; border-radius: 8px; padding: .8rem 1rem; margin-bottom: 1rem; font-size: .9rem; }

  .center-block { display: flex; flex-direction: column; align-items: center; gap: 1rem; text-align: center; }
  .big-icon { font-size: 3.5rem; animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }
  .lead { font-size: 1.05rem; color: #ddd; margin: 0; }
  .sub  { font-size: .9rem; color: #888; margin: 0; }

  .hud { display: flex; gap: 1.2rem; margin-bottom: 1rem; color: #aaa; font-size: .9rem; }
  .hud strong { color: #00aaff; }

  .chat-wrap { display: flex; flex-direction: column; gap: .6rem; max-height: 340px; overflow-y: auto; padding: .5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,.07); border-radius: 10px; background: rgba(0,0,0,.3); }
  .msg { display: flex; align-items: flex-start; gap: .5rem; }
  .msg-user { flex-direction: row-reverse; }
  .avatar { font-size: 1.2rem; flex-shrink: 0; }
  .bubble { padding: .6rem .9rem; border-radius: 12px; max-width: 80%; line-height: 1.45; font-size: .95rem; }
  .msg-user .bubble { background: rgba(0,170,255,.2); border: 1px solid rgba(0,170,255,.3); color: #e0f0ff; }
  .msg-bot  .bubble { background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.1); color: #ddd; }
  .typing { letter-spacing: 3px; animation: blink 1s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

  .input-row, .guess-row { display: flex; gap: .5rem; margin-bottom: .8rem; }
  .chat-input { flex: 1; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.15); color: #eee; padding: .7rem 1rem; border-radius: 10px; font-size: .95rem; outline: none; }
  .chat-input:focus { border-color: rgba(0,170,255,.5); }
  .send-btn { background: linear-gradient(135deg, #00aaff, #0066cc); color: #fff; border: none; border-radius: 10px; padding: .7rem 1.1rem; cursor: pointer; font-weight: 700; }
  .send-btn:disabled { opacity: .4; cursor: not-allowed; }
  .send-btn.confirm { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; }
  .cancel-btn { background: transparent; border: 1px solid rgba(255,255,255,.2); color: #aaa; border-radius: 10px; padding: .7rem .9rem; cursor: pointer; }

  .action-buttons { display: flex; gap: .7rem; flex-wrap: wrap; }
  .btn-hint, .btn-guess, .btn-giveup { flex: 1; padding: .7rem; border: none; border-radius: 10px; font-size: .9rem; cursor: pointer; font-weight: 600; transition: transform .1s; min-width: 90px; }
  .btn-hint:hover, .btn-guess:hover, .btn-giveup:hover { transform: translateY(-2px); }
  .btn-hint:disabled, .btn-guess:disabled, .btn-giveup:disabled { opacity: .4; cursor: not-allowed; transform: none; }
  .btn-hint   { background: rgba(255,200,0,.15); border: 1px solid rgba(255,200,0,.3); color: #ffd700; }
  .btn-guess  { background: linear-gradient(135deg, #00aaff, #0066cc); color: #fff; }
  .btn-giveup { background: rgba(255,60,60,.15); border: 1px solid rgba(255,60,60,.3); color: #ff6b6b; }

  .secret-reveal { font-size: 1.15rem; color: #ddd; }
  .secret-reveal strong { color: #00aaff; font-size: 1.4rem; }
  .category-badge { background: rgba(0,170,255,.15); border: 1px solid rgba(0,170,255,.3); color: #00aaff; font-size: .75rem; padding: .2rem .6rem; border-radius: 10px; margin-left: .5rem; vertical-align: middle; }
  .result-title { font-size: 1.5rem; color: #00aaff; margin: 0; }
  .score-display { display: flex; gap: 1rem; align-items: center; font-size: 1.4rem; font-weight: 700; color: #00ff88; }
  .vs { color: #555; font-size: 1rem; }
  .result-actions { display: flex; gap: 1rem; }

  .btn-primary { background: linear-gradient(135deg, #00aaff, #0066cc); color: #fff; border: none; border-radius: 10px; padding: .8rem 1.8rem; font-size: 1rem; font-weight: 700; cursor: pointer; }
  .btn-primary:hover { filter: brightness(1.1); }
  .btn-secondary { background: transparent; border: 1px solid rgba(0,170,255,.3); color: #00aaff; border-radius: 10px; padding: .8rem 1.8rem; font-size: 1rem; cursor: pointer; }
  .btn-secondary:hover { background: rgba(0,170,255,.1); }
</style>
