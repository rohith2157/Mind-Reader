<script>
  import { onMount } from 'svelte';
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
  <button class="back-btn" on:click={() => navigate('home')}>← Back</button>

  <div class="card">
    <h2 class="page-title">📊 Stats</h2>

    {#if loading}
      <div class="center-text">Loading stats…</div>
    {:else if error}
      <div class="error-box">{error}</div>
    {:else}

      <!-- Scoreboard -->
      <div class="scoreboard">
        <div class="score-item">
          <span class="score-label">🤖 AI Wins</span>
          <span class="score-val ai">{score.ai_wins}</span>
        </div>
        <div class="score-divider">vs</div>
        <div class="score-item">
          <span class="score-label">🧑 Your Wins</span>
          <span class="score-val user">{score.user_wins}</span>
        </div>
      </div>

      <!-- Model accuracy bar chart -->
      {#if accuracyEntries.length}
        <div class="chart-section">
          <h3 class="chart-title">Model Accuracy</h3>
          {#each accuracyEntries as [model, acc]}
            <div class="bar-row">
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
        <div class="chart-section">
          <h3 class="chart-title">Category Distribution</h3>
          {#each categoryEntries as [cat, count]}
            <div class="bar-row">
              <span class="bar-label">{cat}</span>
              <div class="bar-bg">
                <div class="bar-fill cat" style="width:{(count / maxCategory) * 100}%"></div>
              </div>
              <span class="bar-val">{count}</span>
            </div>
          {/each}
        </div>
      {/if}

      <!-- Recent game history -->
      {#if recentGames.length}
        <div class="chart-section">
          <h3 class="chart-title">Recent Games</h3>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Mode</th>
                  <th>Entity</th>
                  <th>Result</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {#each recentGames as g, i}
                  <tr>
                    <td>{i + 1}</td>
                    <td><span class="mode-badge {g.mode}">{g.mode === 'ai_guesses' ? '🤖 AI' : '🎯 You'}</span></td>
                    <td>{g.entity ?? '—'}</td>
                    <td><span class="result-badge {g.correct ? 'win' : 'loss'}">{g.correct ? 'Win' : 'Loss'}</span></td>
                    <td>{g.score ?? '—'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {:else}
        <p class="center-text dim">No games played yet — go play!</p>
      {/if}

    {/if}
  </div>
</div>

<style>
  .page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 5rem 1rem 2rem; }
  .back-btn { position: fixed; top: 1.2rem; left: 1.2rem; background: rgba(255,200,0,.1); border: 1px solid rgba(255,200,0,.3); color: #ffd700; padding: .5rem 1rem; border-radius: 8px; cursor: pointer; font-size: .9rem; }
  .back-btn:hover { background: rgba(255,200,0,.2); }

  .card { background: rgba(0,0,0,.8); border: 1px solid rgba(255,200,0,.2); border-radius: 20px; padding: 2rem; width: 100%; max-width: 700px; backdrop-filter: blur(8px); }
  .page-title { color: #ffd700; text-align: center; margin: 0 0 1.5rem; font-size: 1.7rem; }

  .error-box { background: rgba(255,60,60,.15); border: 1px solid #ff3c3c; color: #ff6b6b; border-radius: 8px; padding: .8rem 1rem; margin-bottom: 1rem; }
  .center-text { text-align: center; color: #888; padding: 2rem; }
  .dim { color: #555; }

  .scoreboard { display: flex; align-items: center; justify-content: center; gap: 2rem; background: rgba(255,200,0,.05); border: 1px solid rgba(255,200,0,.15); border-radius: 14px; padding: 1.2rem; margin-bottom: 2rem; }
  .score-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .score-label { color: #888; font-size: .8rem; }
  .score-val { font-size: 2rem; font-weight: 700; }
  .score-val.ai   { color: #00ff88; }
  .score-val.user { color: #00aaff; }
  .score-divider { color: #555; font-size: 1.2rem; font-weight: 700; }

  .chart-section { margin-bottom: 2rem; }
  .chart-title { color: #ffd700; font-size: 1rem; margin-bottom: .8rem; text-transform: uppercase; letter-spacing: 1px; }

  .bar-row { display: flex; align-items: center; gap: .8rem; margin-bottom: .5rem; }
  .bar-label { color: #aaa; font-size: .82rem; width: 100px; flex-shrink: 0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
  .bar-bg { flex: 1; height: 20px; background: rgba(255,255,255,.07); border-radius: 10px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 10px; transition: width .5s ease; }
  .bar-fill.acc { background: linear-gradient(90deg, #00ff88, #00ccff); }
  .bar-fill.cat { background: linear-gradient(90deg, #ffd700, #ff8c00); }
  .bar-val { color: #eee; font-size: .82rem; width: 40px; text-align: right; flex-shrink: 0; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: .88rem; }
  th { color: #888; text-align: left; padding: .5rem .8rem; border-bottom: 1px solid rgba(255,255,255,.1); font-weight: 600; }
  td { color: #ccc; padding: .5rem .8rem; border-bottom: 1px solid rgba(255,255,255,.05); }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,.03); }

  .mode-badge { font-size: .8rem; padding: .2rem .5rem; border-radius: 6px; }
  .mode-badge.ai_guesses { background: rgba(0,255,136,.12); color: #00ff88; }
  .mode-badge.user_guesses { background: rgba(0,170,255,.12); color: #00aaff; }

  .result-badge { font-size: .78rem; padding: .2rem .5rem; border-radius: 6px; font-weight: 600; }
  .result-badge.win  { background: rgba(0,255,136,.15); color: #00ff88; }
  .result-badge.loss { background: rgba(255,60,60,.15); color: #ff6b6b; }
</style>
