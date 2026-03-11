<script>
  import { fade } from 'svelte/transition';
  import Home        from './pages/Home.svelte';
  import AIGuesses   from './pages/AIGuesses.svelte';
  import UserGuesses from './pages/UserGuesses.svelte';
  import Stats       from './pages/Stats.svelte';

  let page = 'home';
  function navigate(dest) { page = dest; }
</script>

{#if page === 'home'}
  <div in:fade={{ duration: 300 }}><Home {navigate} /></div>
{:else if page === 'ai'}
  <div in:fade={{ duration: 300 }}><AIGuesses {navigate} /></div>
{:else if page === 'user'}
  <div in:fade={{ duration: 300 }}><UserGuesses {navigate} /></div>
{:else if page === 'stats'}
  <div in:fade={{ duration: 300 }}><Stats {navigate} /></div>
{/if}
