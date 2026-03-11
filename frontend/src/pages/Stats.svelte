<script>
  import { onMount } from 'svelte';
  import { fade, scale, slide } from 'svelte/transition';
  import { getStats, getScore } from '../lib/api.js';

  export let navigate;

  let stats   = null;
  let score   = { ai_wins: 0, user_wins: 0 };
  let loading = true;
  let error   = '';

  onMount(async () => {
    try {
      const [s, sc] = await Promise.all([getStats(), getScore()]);
      stats = s.stats;
      score = sc;
    } catch (e) {
      error = e.message;
    }
    loading = false;
  });

  // Derive chart data from stats
  $: accuracyEntries = stats ? Object.entries(stats.model_accuracy ?? {}) : [];
  $: categoryEntries = stats ? Object.entries(stats.category_distribution ?? {}) : [];
  $: maxAccuracy     = accuracyEntries.length ? Math.max(...accuracyEntries.map(([,v]) => v)) : 1;
  $: maxCategory     = categoryEntries.length ? Math.max(...categoryEntries.map(([,v]) => v)) : 1;
  $: recentGames     = stats?.game_history?.slice(-10).reverse() ?? [];
</script>

<div class="page">
  <button class="back-btn" on:click={() => navigate('home')}>
    <span class="icon">←</span> Back
  </button>

  <div class="card" in:scale={{ duration: 400, start: 0.95 }}>
    <h2 class="page-title">📊 OVERALL STATISTICS</h2>

    {#if loading}
      <div class="center-text" in:fade>
        <div class="loading-spinner"></div>
        Downloading Global Data…
      </div>
    {:else if error}
      <div class="error-box" transition:slide>{error}</div>
    {:else}

      <!-- Scoreboard -->
      <div class="scoreboard" in:fade={{ delay: 100 }}>
        <div class="score-item">
          <span class="score-label">🤖 AI WINS</span>
          <span class="score-val ai-score">{score.ai_wins}</span>
        </div>
        <div class="score-divider">vs</div>
        <div class="score-item">
          <span class="score-label">🧑 USER WINS</span>
          <span class="score-val user-score">{score.user_wins}</span>
        </div>
      </div>

      <div class="chart-grid">
        <!-- Model accuracy bar chart -->
        {#if accuracyEntries.length}
          <div class="chart-section" in:slide={{ delay: 200 }}>
            <h3 class="chart-title">AI Engine Accuracy</h3>
            {#each accuracyEntries as [model, acc], i}
              <div class="bar-row" in:fade={{ delay: 300 + (i * 100) }}>
                <span class="bar-label">{model.toUpperCase()}</span>
                <div class="bar-bg">
                  <div class="bar-fill acc" style="width:{(acc / maxAccuracy) * 100}%"></div>
                </div>
                <span class="bar-val">{(acc * 100).toFixed(1)}%</span>
              </div>
            {/each}
          </div>
        {/if}

        <!-- Category distribution bar chart -->
        {#if categoryEntries.length}
          <div class="chart-section" in:slide={{ delay: 200 }}>
            <h3 class="chart-title">Category Distribution</h3>
            {#each categoryEntries as [cat, count], i}
              <div class="bar-row" in:fade={{ delay: 300 + (i * 100) }}>
                <span class="bar-label">{cat}</span>
                <div class="bar-bg">
                  <div class="bar-fill cat" style="width:{(count / maxCategory) * 100}%"></div>
                </div>
                <span class="bar-val">{count}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Recent game history -->
      {#if recentGames.length}
        <div class="chart-section" in:fade={{ delay: 400 }}>
          <h3 class="chart-title">Recent Connections</h3>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Core Mode</th>
                  <th>Target Entity</th>
                  <th>Result Code</th>
                  <th>Score / Cost</th>
                </tr>
              </thead>
              <tbody>
                {#each recentGames as g, i}
                  <tr in:fade={{ delay: 500 + (i * 50) }}>
                    <td class="index-cell">{i + 1}</td>
                    <td><span class="mode-badge {g.mode}">{g.mode === 'ai_guesses' ? '🤖 AI Core' : '🎯 User Uplink'}</span></td>
                    <td class="entity-cell">{g.entity ?? '—'}</td>
                    <td><span class="result-badge {g.correct ? 'win' : 'loss'}">{g.correct ? 'SUCCESS' : 'FAILURE'}</span></td>
                    <td>{g.score ?? '—'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {:else}
        <p class="center-text dim" in:fade>No connection logs found. Initialize a game sequence to generate data.</p>
      {/if}

    {/if}
  </div>
</div>

<style>
  .page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 5rem 1rem 2rem; position: relative; z-index: 10; }
  
  .back-btn { 
    position: fixed; top: 1.5rem; left: 1.5rem; 
    background: rgba(225, 0, 255, 0.05); 
    border: 1px solid rgba(225, 0, 255, 0.2); 
    color: var(--c-accent-light); 
    padding: 0.6rem 1.2rem; 
    border-radius: 12px; 
    cursor: pointer; 
    font-size: 0.95rem; font-weight: 600;
    transition: all 0.2s;
    backdrop-filter: blur(5px);
    display: flex; align-items: center; gap: 8px;
  }
  .back-btn:hover { background: rgba(225, 0, 255, 0.15); transform: translateX(-3px); box-shadow: 0 0 15px rgba(225,0,255,0.2); }

  .card { 
    background: var(--c-card); border: 1px solid var(--c-card-border); 
    border-radius: 24px; padding: 2.5rem; width: 100%; max-width: 850px; 
    backdrop-filter: blur(20px); 
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
  }
  
  .page-title { 
    font-family: var(--font-display); 
    color: var(--c-accent-light); 
    text-align: center; margin: 0 0 2rem; 
    font-size: 2rem; font-weight: 800;
    text-shadow: 0 0 15px rgba(225,0,255,0.3);
    letter-spacing: 2px;
  }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid rgba(255,60,60,.4); color: #ff6b6b; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; text-align: center; font-weight: 600; }
  
  .center-text { text-align: center; color: var(--c-text-muted); padding: 3rem; display: flex; flex-direction: column; align-items: center; gap: 1rem; font-family: var(--font-display); font-size: 1.1rem; letter-spacing: 1px; }
  .dim { opacity: 0.6; }

  .loading-spinner {
    width: 40px; height: 40px;
    border: 3px solid rgba(0,242,254,0.1);
    border-top-color: var(--c-primary);
    border-radius: 50%;
    animation: spin 1s infinite linear;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .scoreboard { 
    display: flex; align-items: center; justify-content: center; gap: 4rem; 
    background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); 
    border-radius: 16px; padding: 1.5rem; margin-bottom: 2.5rem; 
    box-shadow: inset 0 0 30px rgba(0,0,0,0.5);
  }
  .score-item { display: flex; flex-direction: column; align-items: center; gap: 6px; }
  .score-label { color: var(--c-text-muted); font-size: .85rem; font-weight: 700; letter-spacing: 1.5px; }
  .score-val { font-size: 3rem; font-family: var(--font-display); font-weight: 800; line-height: 1; }
  
  .ai-score   { color: var(--c-primary); text-shadow: 0 0 20px rgba(0,242,254,0.4); }
  .user-score { color: var(--c-accent-light); text-shadow: 0 0 20px rgba(225,0,255,0.4); }
  .score-divider { color: var(--c-text-muted); font-size: 1.5rem; font-weight: 700; font-family: var(--font-display); opacity: 0.5; }

  .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2.5rem; }
  
  .chart-section { background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
  .chart-title { color: var(--c-text); font-family: var(--font-display); font-size: 1.1rem; margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 1.5px; }

  .bar-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.8rem; }
  .bar-label { color: var(--c-text-muted); font-size: .85rem; font-weight: 600; width: 110px; flex-shrink: 0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; letter-spacing: 0.5px; }
  .bar-bg { flex: 1; height: 12px; background: rgba(255,255,255,.05); border-radius: 6px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 6px; transition: width 1s cubic-bezier(0.2, 0.8, 0.2, 1); }
  
  .bar-fill.acc { background: linear-gradient(90deg, var(--c-primary-dark), var(--c-primary)); box-shadow: 0 0 10px rgba(0,242,254,0.3); }
  .bar-fill.cat { background: linear-gradient(90deg, var(--c-accent), var(--c-accent-light)); box-shadow: 0 0 10px rgba(225,0,255,0.3); }
  
  .bar-val { color: var(--c-text); font-size: .85rem; font-weight: 700; width: 45px; text-align: right; flex-shrink: 0; }

  .table-wrap { overflow-x: auto; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.3); }
  table { width: 100%; border-collapse: collapse; font-size: .9rem; text-align: left; }
  th { color: var(--c-text-muted); padding: 1rem 1.2rem; border-bottom: 1px solid rgba(255,255,255,.1); font-weight: 700; font-family: var(--font-display); letter-spacing: 1px; text-transform: uppercase; font-size: 0.8rem; }
  td { color: var(--c-text); padding: 0.8rem 1.2rem; border-bottom: 1px solid rgba(255,255,255,.05); vertical-align: middle; }
  
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,.03); }

  .index-cell { color: var(--c-text-muted); font-family: var(--font-display); font-weight: 700; }
  .entity-cell { font-weight: 600; color: #fff; }

  .mode-badge { font-size: .75rem; font-weight: 700; padding: .3rem .6rem; border-radius: 6px; letter-spacing: 0.5px; }
  .mode-badge.ai_guesses { background: rgba(0, 242, 254, 0.1); border: 1px solid rgba(0, 242, 254, 0.3); color: var(--c-primary); }
  .mode-badge.user_guesses { background: rgba(225, 0, 255, 0.1); border: 1px solid rgba(225, 0, 255, 0.3); color: var(--c-accent-light); }

  .result-badge { font-size: .75rem; padding: .3rem .6rem; border-radius: 6px; font-weight: 700; letter-spacing: 1px; }
  .result-badge.win  { background: rgba(0, 255, 136, 0.1) ; border: 1px solid rgba(0, 255, 136, 0.3); color: #00ff88; }
  .result-badge.loss { background: rgba(255, 68, 85, 0.1); border: 1px solid rgba(255, 68, 85, 0.3); color: #ff4455; }
</style>
