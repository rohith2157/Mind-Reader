<script>
  import { onMount } from 'svelte';
  import { getScore } from '../lib/api.js';

  export let navigate;

  let score = { ai_wins: 0, user_wins: 0 };
  let canvas;
  let animFrame;

  onMount(async () => {
    // Fetch scoreboard
    try { score = await getScore(); } catch (_) {}

    // Matrix rain
    const ctx = canvas.getContext('2d');
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;

    const cols = Math.floor(canvas.width / 20);
    const drops = Array(cols).fill(1);
    const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ0123456789ABCDEF';

    function draw() {
      ctx.fillStyle = 'rgba(0,0,0,0.04)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#0f0';
      ctx.font = '15px monospace';
      drops.forEach((y, i) => {
        const ch = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(ch, i * 20, y * 20);
        if (y * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      });
      animFrame = requestAnimationFrame(draw);
    }
    draw();

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener('resize', resize);
    };
  });
</script>

<canvas bind:this={canvas} class="matrix-canvas"></canvas>

<div class="home-wrap">
  <div class="brain-ring ring1"></div>
  <div class="brain-ring ring2"></div>
  <div class="brain-ring ring3"></div>

  <div class="hero">
    <div class="brain-icon">🧠</div>
    <h1 class="title">AI Mind Reader</h1>
    <p class="subtitle">Can the AI read your mind? Or can you outsmart it?</p>

    <div class="mode-buttons">
      <button class="btn btn-ai" on:click={() => navigate('ai')}>
        <span class="btn-icon">🤖</span>
        <span>AI GUESSES</span>
        <small>Think of something — AI will figure it out</small>
      </button>
      <button class="btn btn-user" on:click={() => navigate('user')}>
        <span class="btn-icon">🎯</span>
        <span>YOU GUESS</span>
        <small>Ask yes/no questions to find the secret</small>
      </button>
    </div>

    <div class="scoreboard">
      <div class="score-item">
        <span class="score-label">🤖 AI Wins</span>
        <span class="score-val">{score.ai_wins}</span>
      </div>
      <div class="score-divider">vs</div>
      <div class="score-item">
        <span class="score-label">🧑 Your Wins</span>
        <span class="score-val">{score.user_wins}</span>
      </div>
    </div>

    <button class="btn-stats" on:click={() => navigate('stats')}>📊 View Stats</button>
  </div>
</div>

<style>
  .matrix-canvas {
    position: fixed; inset: 0;
    z-index: 0;
    opacity: 0.35;
  }
  .home-wrap {
    position: relative; z-index: 1;
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
  }
  .brain-ring {
    position: fixed;
    border-radius: 50%;
    border: 1px solid rgba(0,255,136,0.15);
    animation: spin linear infinite;
    pointer-events: none;
  }
  .ring1 { width: 500px; height: 500px; top: 50%; left: 50%; margin: -250px 0 0 -250px; animation-duration: 20s; }
  .ring2 { width: 700px; height: 700px; top: 50%; left: 50%; margin: -350px 0 0 -350px; animation-duration: 35s; animation-direction: reverse; }
  .ring3 { width: 900px; height: 900px; top: 50%; left: 50%; margin: -450px 0 0 -450px; animation-duration: 50s; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .hero {
    background: rgba(0,0,0,0.75);
    border: 1px solid rgba(0,255,136,0.25);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    text-align: center;
    max-width: 620px;
    width: 100%;
    backdrop-filter: blur(6px);
  }
  .brain-icon { font-size: 4rem; animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.12)} }
  .title { font-size: 2.4rem; color: #00ff88; margin: 0.5rem 0; letter-spacing: 2px; }
  .subtitle { color: #aaa; margin-bottom: 2rem; }

  .mode-buttons { display: flex; gap: 1.2rem; justify-content: center; flex-wrap: wrap; margin-bottom: 2rem; }
  .btn {
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    padding: 1.1rem 1.8rem;
    border: none; border-radius: 12px; cursor: pointer;
    font-size: 1rem; font-weight: 700; letter-spacing: 1px;
    transition: transform .15s, box-shadow .15s;
    min-width: 180px;
  }
  .btn:hover { transform: translateY(-3px); }
  .btn small { font-size: 0.72rem; font-weight: 400; opacity: 0.85; }
  .btn-icon { font-size: 1.6rem; }
  .btn-ai   { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; box-shadow: 0 0 20px rgba(0,255,136,.35); }
  .btn-user { background: linear-gradient(135deg, #00aaff, #0066cc); color: #fff; box-shadow: 0 0 20px rgba(0,170,255,.35); }

  .scoreboard {
    display: flex; align-items: center; justify-content: center; gap: 1.5rem;
    background: rgba(0,255,136,0.06);
    border: 1px solid rgba(0,255,136,0.15);
    border-radius: 12px;
    padding: 1rem 2rem;
    margin-bottom: 1.5rem;
  }
  .score-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .score-label { color: #888; font-size: 0.8rem; }
  .score-val { font-size: 2rem; font-weight: 700; color: #00ff88; }
  .score-divider { color: #555; font-size: 1.2rem; font-weight: 700; }

  .btn-stats {
    background: transparent;
    border: 1px solid rgba(0,255,136,0.3);
    color: #00ff88;
    padding: 0.6rem 1.4rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background .15s;
  }
  .btn-stats:hover { background: rgba(0,255,136,0.1); }
</style>
