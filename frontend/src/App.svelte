<script>
  import Home        from './pages/Home.svelte';
  import AIGuesses   from './pages/AIGuesses.svelte';
  import UserGuesses from './pages/UserGuesses.svelte';
  import Stats       from './pages/Stats.svelte';

  let page = 'home';
  function navigate(dest) { page = dest; }
</script>

{#if page === 'home'}
  <Home {navigate} />
{:else if page === 'ai'}
  <AIGuesses {navigate} />
{:else if page === 'user'}
  <UserGuesses {navigate} />
{:else if page === 'stats'}
  <Stats {navigate} />
{/if}
