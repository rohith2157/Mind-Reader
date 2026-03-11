<script>
  import { onMount } from 'svelte';
  import { getScore } from '../lib/api.js';

  export let navigate;
  let score = { ai_wins: 0, user_wins: 0 };

  onMount(async () => {
    try { score = await getScore(); } catch (_) {}
  });
</script>

<div class="home-wrap">
  <!-- Glowing Background Orbs -->
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>

  <div class="hero">
    <div class="brain-icon">🧠</div>
    <h1 class="title">Mind Reader AI</h1>
    <p class="subtitle">Can the AI read your mind? Or can you outsmart it?</p>

    <div class="mode-buttons">
      <button class="btn btn-ai" on:click={() => navigate('ai')}>
        <span class="btn-icon">🤖</span>
        <span>AI GUESSES</span>
        <small>Think of something — AI will figure it out</small>
        <div class="btn-glow"></div>
      </button>
      <button class="btn btn-user" on:click={() => navigate('user')}>
        <span class="btn-icon">🎯</span>
        <span>YOU GUESS</span>
        <small>Ask yes/no questions to find the secret</small>
        <div class="btn-glow"></div>
      </button>
    </div>

    <div class="scoreboard">
      <div class="score-item">
        <span class="score-label">🤖 AI Wins</span>
        <span class="score-val ai-score">{score.ai_wins}</span>
      </div>
      <div class="score-divider">vs</div>
      <div class="score-item">
        <span class="score-label">🧑 Your Wins</span>
        <span class="score-val user-score">{score.user_wins}</span>
      </div>
    </div>

    <button class="btn-stats" on:click={() => navigate('stats')}>📊 View Stats</button>
  </div>
</div>

<style>
  .home-wrap {
    position: relative; 
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
  }

  /* Abstract Glowing Background */
  .orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
    opacity: 0.5;
    animation: drift 15s infinite alternate ease-in-out;
  }
  .orb-1 {
    width: 400px; height: 400px;
    background: var(--c-primary);
    top: -100px; left: -100px;
  }
  .orb-2 {
    width: 500px; height: 500px;
    background: var(--c-accent);
    bottom: -150px; right: -150px;
    animation-delay: -5s;
  }
  @keyframes drift {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(100px, 50px) scale(1.1); }
  }

  .hero {
    position: relative;
    z-index: 10;
    background: var(--c-card);
    border: 1px solid var(--c-card-border);
    border-radius: 24px;
    padding: 3.5rem 3rem;
    text-align: center;
    max-width: 680px;
    width: 90%;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
  }

  .brain-icon { 
    font-size: 4.5rem; 
    animation: float 4s ease-in-out infinite; 
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 0 20px rgba(0, 242, 254, 0.4));
  }
  @keyframes float { 
    0%,100%{transform:translateY(0)} 
    50%{transform:translateY(-15px)} 
  }

  .title { 
    font-family: var(--font-display);
    font-size: 3rem; 
    font-weight: 800;
    background: linear-gradient(135deg, #fff, var(--c-primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0rem 0 0.5rem; 
    letter-spacing: -1px; 
  }
  .subtitle { 
    color: var(--c-text-muted); 
    font-size: 1.1rem;
    margin-bottom: 2.5rem; 
  }

  .mode-buttons { 
    display: flex; gap: 1.5rem; 
    justify-content: center; flex-wrap: wrap; 
    margin-bottom: 2.5rem; 
  }
  
  .btn {
    position: relative;
    overflow: hidden;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    padding: 1.5rem 2rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; cursor: pointer;
    font-size: 1.1rem; font-weight: 700; letter-spacing: 1px;
    transition: all .3s cubic-bezier(0.2, 0.8, 0.2, 1);
    min-width: 200px; color: #fff;
    backdrop-filter: blur(10px);
  }
  
  .btn:hover { 
    transform: translateY(-5px) scale(1.02); 
    border-color: rgba(255,255,255,0.3);
  }
  
  .btn small { 
    font-size: 0.75rem; font-weight: 400; 
    color: var(--c-text-muted); 
    margin-top: 5px;
  }
  .btn-icon { font-size: 2rem; z-index: 2; position: relative; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));}
  .btn span { z-index: 2; position: relative; font-family: var(--font-display); }
  .btn small { z-index: 2; position: relative; }

  .btn-glow {
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: 1;
  }
  .btn-ai .btn-glow { background: radial-gradient(circle at top, rgba(0,242,254,0.3) 0%, transparent 70%); }
  .btn-user .btn-glow { background: radial-gradient(circle at top, rgba(127,0,255,0.3) 0%, transparent 70%); }
  
  .btn:hover .btn-glow { opacity: 1; }

  .scoreboard {
    display: flex; align-items: center; justify-content: center; gap: 2.5rem;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1.5rem 3rem;
    margin-bottom: 2rem;
  }
  .score-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .score-label { color: var(--c-text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
  .score-val { font-size: 2.5rem; font-weight: 800; font-family: var(--font-display); }
  
  .ai-score { color: var(--c-primary); text-shadow: 0 0 20px rgba(0,242,254,0.4); }
  .user-score { color: var(--c-accent-light); text-shadow: 0 0 20px rgba(225,0,255,0.4); }
  
  .score-divider { color: var(--c-text-muted); font-size: 1.2rem; font-weight: 600; opacity: 0.5; }

  .btn-stats {
    background: transparent;
    border: 1px solid var(--c-card-border);
    color: var(--c-text);
    padding: 0.8rem 2rem;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.95rem; font-weight: 500;
    transition: all .2s;
  }
  .btn-stats:hover { 
    background: rgba(255,255,255,0.05); 
    color: var(--c-primary);
    border-color: rgba(0,242,254,0.4);
  }
</style>
